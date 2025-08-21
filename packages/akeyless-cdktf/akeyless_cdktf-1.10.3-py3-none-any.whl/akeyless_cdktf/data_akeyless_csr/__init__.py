'''
# `data_akeyless_csr`

Refer to the Terraform Registry for docs: [`data_akeyless_csr`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr).
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


class DataAkeylessCsr(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessCsr.DataAkeylessCsr",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr akeyless_csr}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        common_name: builtins.str,
        name: builtins.str,
        alg: typing.Optional[builtins.str] = None,
        alt_names: typing.Optional[builtins.str] = None,
        certificate_type: typing.Optional[builtins.str] = None,
        city: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        critical: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dep: typing.Optional[builtins.str] = None,
        email_addresses: typing.Optional[builtins.str] = None,
        generate_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        ip_addresses: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        org: typing.Optional[builtins.str] = None,
        split_level: typing.Optional[jsii.Number] = None,
        state: typing.Optional[builtins.str] = None,
        uri_sans: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr akeyless_csr} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param common_name: The common name to be included in the CSR certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#common_name DataAkeylessCsr#common_name}
        :param name: The classic key name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#name DataAkeylessCsr#name}
        :param alg: The algorithm (RSA/Elliptic-curve) to use for generating the new key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#alg DataAkeylessCsr#alg}
        :param alt_names: A comma-separated list of dns alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#alt_names DataAkeylessCsr#alt_names}
        :param certificate_type: The certificate type to be included in the CSR certificate (ssl-client/ssl-server/certificate-signing). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#certificate_type DataAkeylessCsr#certificate_type}
        :param city: The city to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#city DataAkeylessCsr#city}
        :param country: The country to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#country DataAkeylessCsr#country}
        :param critical: Add critical to the key usage extension (will be false if not added). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#critical DataAkeylessCsr#critical}
        :param dep: The department to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#dep DataAkeylessCsr#dep}
        :param email_addresses: A comma-separated list of email addresses alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#email_addresses DataAkeylessCsr#email_addresses}
        :param generate_key: Generate a new classic key for the csr. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#generate_key DataAkeylessCsr#generate_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#id DataAkeylessCsr#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_addresses: A comma-separated list of ip addresses alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#ip_addresses DataAkeylessCsr#ip_addresses}
        :param key_type: The type of the key to generate (classic-key/dfc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#key_type DataAkeylessCsr#key_type}
        :param org: The organization to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#org DataAkeylessCsr#org}
        :param split_level: The number of fragments that the item will be split into (not includes customer fragment, relevant only for dfc keys). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#split_level DataAkeylessCsr#split_level}
        :param state: The state to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#state DataAkeylessCsr#state}
        :param uri_sans: A comma-separated list of uri alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#uri_sans DataAkeylessCsr#uri_sans}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8226a48ed8482e8cf1012a3f880b5e6be7752d9a29f16713cd8f402282bb3b8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAkeylessCsrConfig(
            common_name=common_name,
            name=name,
            alg=alg,
            alt_names=alt_names,
            certificate_type=certificate_type,
            city=city,
            country=country,
            critical=critical,
            dep=dep,
            email_addresses=email_addresses,
            generate_key=generate_key,
            id=id,
            ip_addresses=ip_addresses,
            key_type=key_type,
            org=org,
            split_level=split_level,
            state=state,
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
        '''Generates CDKTF code for importing a DataAkeylessCsr resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataAkeylessCsr to import.
        :param import_from_id: The id of the existing DataAkeylessCsr that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataAkeylessCsr to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f5f4792b7916bdd7e2f37ffcc891518c53283213deebbd1aeaa27ec16dde19e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlg")
    def reset_alg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlg", []))

    @jsii.member(jsii_name="resetAltNames")
    def reset_alt_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAltNames", []))

    @jsii.member(jsii_name="resetCertificateType")
    def reset_certificate_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateType", []))

    @jsii.member(jsii_name="resetCity")
    def reset_city(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCity", []))

    @jsii.member(jsii_name="resetCountry")
    def reset_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountry", []))

    @jsii.member(jsii_name="resetCritical")
    def reset_critical(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCritical", []))

    @jsii.member(jsii_name="resetDep")
    def reset_dep(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDep", []))

    @jsii.member(jsii_name="resetEmailAddresses")
    def reset_email_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailAddresses", []))

    @jsii.member(jsii_name="resetGenerateKey")
    def reset_generate_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenerateKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIpAddresses")
    def reset_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddresses", []))

    @jsii.member(jsii_name="resetKeyType")
    def reset_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyType", []))

    @jsii.member(jsii_name="resetOrg")
    def reset_org(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrg", []))

    @jsii.member(jsii_name="resetSplitLevel")
    def reset_split_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSplitLevel", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

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
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="algInput")
    def alg_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algInput"))

    @builtins.property
    @jsii.member(jsii_name="altNamesInput")
    def alt_names_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "altNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateTypeInput")
    def certificate_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cityInput")
    def city_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cityInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="countryInput")
    def country_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryInput"))

    @builtins.property
    @jsii.member(jsii_name="criticalInput")
    def critical_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "criticalInput"))

    @builtins.property
    @jsii.member(jsii_name="depInput")
    def dep_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "depInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAddressesInput")
    def email_addresses_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="generateKeyInput")
    def generate_key_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "generateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ipAddressesInput")
    def ip_addresses_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipAddressesInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="orgInput")
    def org_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orgInput"))

    @builtins.property
    @jsii.member(jsii_name="splitLevelInput")
    def split_level_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "splitLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="uriSansInput")
    def uri_sans_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="alg")
    def alg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alg"))

    @alg.setter
    def alg(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f0a27a9afa23fae7c505af666b487a08eef37ace373c5be0c395df2ebf738e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alg", value)

    @builtins.property
    @jsii.member(jsii_name="altNames")
    def alt_names(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "altNames"))

    @alt_names.setter
    def alt_names(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1806ce13d63a0c021ba5e80001502b2d53f3b269a3067a9d77b94b8491bd8fa5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "altNames", value)

    @builtins.property
    @jsii.member(jsii_name="certificateType")
    def certificate_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateType"))

    @certificate_type.setter
    def certificate_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5490cd2c7dca42f8878e8e01899c4f8871ca8ce3f243dc12a423f2434a7b0e48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateType", value)

    @builtins.property
    @jsii.member(jsii_name="city")
    def city(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "city"))

    @city.setter
    def city(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcf80f85599746c68957461ee7df35bccd3e2706f786985c23c8e9e883fc3260)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "city", value)

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c1d88a9c7b7a4c7413c672842b99a6de7930c205c9405713c0914c7a6662575)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value)

    @builtins.property
    @jsii.member(jsii_name="country")
    def country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "country"))

    @country.setter
    def country(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d24e29223b450b3c5067d3c217dcdc565b6a7dad56ff8ea7ad9cbd208edde5e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "country", value)

    @builtins.property
    @jsii.member(jsii_name="critical")
    def critical(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "critical"))

    @critical.setter
    def critical(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8110f2ec52e029aae78bad128734aaed9bdc01ffb2aafec687384ab9ee0d0208)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "critical", value)

    @builtins.property
    @jsii.member(jsii_name="dep")
    def dep(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dep"))

    @dep.setter
    def dep(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4238438ef2d030c63ac03590a0a7140c39b01bb5b33076695b2770d0c9fcc383)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dep", value)

    @builtins.property
    @jsii.member(jsii_name="emailAddresses")
    def email_addresses(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailAddresses"))

    @email_addresses.setter
    def email_addresses(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f590bdba275aab279736c1e9e4396089002d68ef5bd62356be473056bb54df8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAddresses", value)

    @builtins.property
    @jsii.member(jsii_name="generateKey")
    def generate_key(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "generateKey"))

    @generate_key.setter
    def generate_key(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2670f504960c7cff2658dda6562866c8779366a171f29413d4bb2ec901081451)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generateKey", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d73d515b1566d94225256ca78af4bb6d269fe8eb11d74d4f27891ee53fa4940c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddresses"))

    @ip_addresses.setter
    def ip_addresses(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8cba3887c8b54648821042f281da4f499f3298d87d0cffad4ba6dc3076403d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipAddresses", value)

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09c797cbb34317d10d1dffcc1ca1d10962d95cce143afa0951bde7676e2f4bd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d312973105509eab3c5eabe432777a32d15ea5aa744ca092748701d42ffde7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="org")
    def org(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "org"))

    @org.setter
    def org(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d31d4ddd0bc76775ee54fc7e5b29873a631c6921b0948a665536e93476b5d126)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "org", value)

    @builtins.property
    @jsii.member(jsii_name="splitLevel")
    def split_level(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "splitLevel"))

    @split_level.setter
    def split_level(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c65306052a261d1730253731b64b3bb3c9143eedf4f9ec699fef3690d396068)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "splitLevel", value)

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__189d27b574263edd433c64e5a92832b12cfaa4253d135576b81bee8f025bd5ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value)

    @builtins.property
    @jsii.member(jsii_name="uriSans")
    def uri_sans(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uriSans"))

    @uri_sans.setter
    def uri_sans(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1a323244eb6f455d5d010fbe7fdcbcb5611a311ab814a656ec5e3e839e82158)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uriSans", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessCsr.DataAkeylessCsrConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "common_name": "commonName",
        "name": "name",
        "alg": "alg",
        "alt_names": "altNames",
        "certificate_type": "certificateType",
        "city": "city",
        "country": "country",
        "critical": "critical",
        "dep": "dep",
        "email_addresses": "emailAddresses",
        "generate_key": "generateKey",
        "id": "id",
        "ip_addresses": "ipAddresses",
        "key_type": "keyType",
        "org": "org",
        "split_level": "splitLevel",
        "state": "state",
        "uri_sans": "uriSans",
    },
)
class DataAkeylessCsrConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        common_name: builtins.str,
        name: builtins.str,
        alg: typing.Optional[builtins.str] = None,
        alt_names: typing.Optional[builtins.str] = None,
        certificate_type: typing.Optional[builtins.str] = None,
        city: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        critical: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dep: typing.Optional[builtins.str] = None,
        email_addresses: typing.Optional[builtins.str] = None,
        generate_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        ip_addresses: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        org: typing.Optional[builtins.str] = None,
        split_level: typing.Optional[jsii.Number] = None,
        state: typing.Optional[builtins.str] = None,
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
        :param common_name: The common name to be included in the CSR certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#common_name DataAkeylessCsr#common_name}
        :param name: The classic key name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#name DataAkeylessCsr#name}
        :param alg: The algorithm (RSA/Elliptic-curve) to use for generating the new key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#alg DataAkeylessCsr#alg}
        :param alt_names: A comma-separated list of dns alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#alt_names DataAkeylessCsr#alt_names}
        :param certificate_type: The certificate type to be included in the CSR certificate (ssl-client/ssl-server/certificate-signing). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#certificate_type DataAkeylessCsr#certificate_type}
        :param city: The city to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#city DataAkeylessCsr#city}
        :param country: The country to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#country DataAkeylessCsr#country}
        :param critical: Add critical to the key usage extension (will be false if not added). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#critical DataAkeylessCsr#critical}
        :param dep: The department to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#dep DataAkeylessCsr#dep}
        :param email_addresses: A comma-separated list of email addresses alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#email_addresses DataAkeylessCsr#email_addresses}
        :param generate_key: Generate a new classic key for the csr. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#generate_key DataAkeylessCsr#generate_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#id DataAkeylessCsr#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param ip_addresses: A comma-separated list of ip addresses alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#ip_addresses DataAkeylessCsr#ip_addresses}
        :param key_type: The type of the key to generate (classic-key/dfc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#key_type DataAkeylessCsr#key_type}
        :param org: The organization to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#org DataAkeylessCsr#org}
        :param split_level: The number of fragments that the item will be split into (not includes customer fragment, relevant only for dfc keys). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#split_level DataAkeylessCsr#split_level}
        :param state: The state to be included in the CSR. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#state DataAkeylessCsr#state}
        :param uri_sans: A comma-separated list of uri alternative names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#uri_sans DataAkeylessCsr#uri_sans}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__897e82c2c07639afbb38c569b6bfe4a0d03f0729f42fec8fdd4f20b143434a40)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument alg", value=alg, expected_type=type_hints["alg"])
            check_type(argname="argument alt_names", value=alt_names, expected_type=type_hints["alt_names"])
            check_type(argname="argument certificate_type", value=certificate_type, expected_type=type_hints["certificate_type"])
            check_type(argname="argument city", value=city, expected_type=type_hints["city"])
            check_type(argname="argument country", value=country, expected_type=type_hints["country"])
            check_type(argname="argument critical", value=critical, expected_type=type_hints["critical"])
            check_type(argname="argument dep", value=dep, expected_type=type_hints["dep"])
            check_type(argname="argument email_addresses", value=email_addresses, expected_type=type_hints["email_addresses"])
            check_type(argname="argument generate_key", value=generate_key, expected_type=type_hints["generate_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument ip_addresses", value=ip_addresses, expected_type=type_hints["ip_addresses"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument org", value=org, expected_type=type_hints["org"])
            check_type(argname="argument split_level", value=split_level, expected_type=type_hints["split_level"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
            check_type(argname="argument uri_sans", value=uri_sans, expected_type=type_hints["uri_sans"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "common_name": common_name,
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
        if alg is not None:
            self._values["alg"] = alg
        if alt_names is not None:
            self._values["alt_names"] = alt_names
        if certificate_type is not None:
            self._values["certificate_type"] = certificate_type
        if city is not None:
            self._values["city"] = city
        if country is not None:
            self._values["country"] = country
        if critical is not None:
            self._values["critical"] = critical
        if dep is not None:
            self._values["dep"] = dep
        if email_addresses is not None:
            self._values["email_addresses"] = email_addresses
        if generate_key is not None:
            self._values["generate_key"] = generate_key
        if id is not None:
            self._values["id"] = id
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if key_type is not None:
            self._values["key_type"] = key_type
        if org is not None:
            self._values["org"] = org
        if split_level is not None:
            self._values["split_level"] = split_level
        if state is not None:
            self._values["state"] = state
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
    def common_name(self) -> builtins.str:
        '''The common name to be included in the CSR certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#common_name DataAkeylessCsr#common_name}
        '''
        result = self._values.get("common_name")
        assert result is not None, "Required property 'common_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The classic key name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#name DataAkeylessCsr#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alg(self) -> typing.Optional[builtins.str]:
        '''The algorithm (RSA/Elliptic-curve) to use for generating the new key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#alg DataAkeylessCsr#alg}
        '''
        result = self._values.get("alg")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def alt_names(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of dns alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#alt_names DataAkeylessCsr#alt_names}
        '''
        result = self._values.get("alt_names")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_type(self) -> typing.Optional[builtins.str]:
        '''The certificate type to be included in the CSR certificate (ssl-client/ssl-server/certificate-signing).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#certificate_type DataAkeylessCsr#certificate_type}
        '''
        result = self._values.get("certificate_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def city(self) -> typing.Optional[builtins.str]:
        '''The city to be included in the CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#city DataAkeylessCsr#city}
        '''
        result = self._values.get("city")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''The country to be included in the CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#country DataAkeylessCsr#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def critical(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Add critical to the key usage extension (will be false if not added).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#critical DataAkeylessCsr#critical}
        '''
        result = self._values.get("critical")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dep(self) -> typing.Optional[builtins.str]:
        '''The department to be included in the CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#dep DataAkeylessCsr#dep}
        '''
        result = self._values.get("dep")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_addresses(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of email addresses alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#email_addresses DataAkeylessCsr#email_addresses}
        '''
        result = self._values.get("email_addresses")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def generate_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Generate a new classic key for the csr.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#generate_key DataAkeylessCsr#generate_key}
        '''
        result = self._values.get("generate_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#id DataAkeylessCsr#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of ip addresses alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#ip_addresses DataAkeylessCsr#ip_addresses}
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''The type of the key to generate (classic-key/dfc).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#key_type DataAkeylessCsr#key_type}
        '''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def org(self) -> typing.Optional[builtins.str]:
        '''The organization to be included in the CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#org DataAkeylessCsr#org}
        '''
        result = self._values.get("org")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def split_level(self) -> typing.Optional[jsii.Number]:
        '''The number of fragments that the item will be split into (not includes customer fragment, relevant only for dfc keys).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#split_level DataAkeylessCsr#split_level}
        '''
        result = self._values.get("split_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''The state to be included in the CSR.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#state DataAkeylessCsr#state}
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uri_sans(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of uri alternative names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/csr#uri_sans DataAkeylessCsr#uri_sans}
        '''
        result = self._values.get("uri_sans")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessCsrConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataAkeylessCsr",
    "DataAkeylessCsrConfig",
]

publication.publish()

def _typecheckingstub__d8226a48ed8482e8cf1012a3f880b5e6be7752d9a29f16713cd8f402282bb3b8(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    common_name: builtins.str,
    name: builtins.str,
    alg: typing.Optional[builtins.str] = None,
    alt_names: typing.Optional[builtins.str] = None,
    certificate_type: typing.Optional[builtins.str] = None,
    city: typing.Optional[builtins.str] = None,
    country: typing.Optional[builtins.str] = None,
    critical: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dep: typing.Optional[builtins.str] = None,
    email_addresses: typing.Optional[builtins.str] = None,
    generate_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    ip_addresses: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    org: typing.Optional[builtins.str] = None,
    split_level: typing.Optional[jsii.Number] = None,
    state: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__0f5f4792b7916bdd7e2f37ffcc891518c53283213deebbd1aeaa27ec16dde19e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f0a27a9afa23fae7c505af666b487a08eef37ace373c5be0c395df2ebf738e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1806ce13d63a0c021ba5e80001502b2d53f3b269a3067a9d77b94b8491bd8fa5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5490cd2c7dca42f8878e8e01899c4f8871ca8ce3f243dc12a423f2434a7b0e48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcf80f85599746c68957461ee7df35bccd3e2706f786985c23c8e9e883fc3260(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c1d88a9c7b7a4c7413c672842b99a6de7930c205c9405713c0914c7a6662575(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d24e29223b450b3c5067d3c217dcdc565b6a7dad56ff8ea7ad9cbd208edde5e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8110f2ec52e029aae78bad128734aaed9bdc01ffb2aafec687384ab9ee0d0208(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4238438ef2d030c63ac03590a0a7140c39b01bb5b33076695b2770d0c9fcc383(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f590bdba275aab279736c1e9e4396089002d68ef5bd62356be473056bb54df8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2670f504960c7cff2658dda6562866c8779366a171f29413d4bb2ec901081451(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d73d515b1566d94225256ca78af4bb6d269fe8eb11d74d4f27891ee53fa4940c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8cba3887c8b54648821042f281da4f499f3298d87d0cffad4ba6dc3076403d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09c797cbb34317d10d1dffcc1ca1d10962d95cce143afa0951bde7676e2f4bd1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14d312973105509eab3c5eabe432777a32d15ea5aa744ca092748701d42ffde7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d31d4ddd0bc76775ee54fc7e5b29873a631c6921b0948a665536e93476b5d126(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c65306052a261d1730253731b64b3bb3c9143eedf4f9ec699fef3690d396068(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__189d27b574263edd433c64e5a92832b12cfaa4253d135576b81bee8f025bd5ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1a323244eb6f455d5d010fbe7fdcbcb5611a311ab814a656ec5e3e839e82158(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__897e82c2c07639afbb38c569b6bfe4a0d03f0729f42fec8fdd4f20b143434a40(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    common_name: builtins.str,
    name: builtins.str,
    alg: typing.Optional[builtins.str] = None,
    alt_names: typing.Optional[builtins.str] = None,
    certificate_type: typing.Optional[builtins.str] = None,
    city: typing.Optional[builtins.str] = None,
    country: typing.Optional[builtins.str] = None,
    critical: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dep: typing.Optional[builtins.str] = None,
    email_addresses: typing.Optional[builtins.str] = None,
    generate_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    ip_addresses: typing.Optional[builtins.str] = None,
    key_type: typing.Optional[builtins.str] = None,
    org: typing.Optional[builtins.str] = None,
    split_level: typing.Optional[jsii.Number] = None,
    state: typing.Optional[builtins.str] = None,
    uri_sans: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
