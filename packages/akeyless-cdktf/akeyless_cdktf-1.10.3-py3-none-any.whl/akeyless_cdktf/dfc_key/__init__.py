'''
# `akeyless_dfc_key`

Refer to the Terraform Registry for docs: [`akeyless_dfc_key`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key).
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


class DfcKey(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dfcKey.DfcKey",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key akeyless_dfc_key}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        alg: builtins.str,
        name: builtins.str,
        auto_rotate: typing.Optional[builtins.str] = None,
        cert_data_base64: typing.Optional[builtins.str] = None,
        certificate_common_name: typing.Optional[builtins.str] = None,
        certificate_country: typing.Optional[builtins.str] = None,
        certificate_format: typing.Optional[builtins.str] = None,
        certificate_locality: typing.Optional[builtins.str] = None,
        certificate_organization: typing.Optional[builtins.str] = None,
        certificate_province: typing.Optional[builtins.str] = None,
        certificate_ttl: typing.Optional[jsii.Number] = None,
        conf_file_data: typing.Optional[builtins.str] = None,
        customer_frg_id: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
        split_level: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key akeyless_dfc_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alg: DFCKey type; options: [AES128GCM, AES256GCM, AES128SIV, AES256SIV, AES128CBC, AES256CBC, RSA1024, RSA2048, RSA3072, RSA4096]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#alg DfcKey#alg}
        :param name: DFCKey name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#name DfcKey#name}
        :param auto_rotate: Whether to automatically rotate every rotation_interval days, or disable existing automatic rotation [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#auto_rotate DfcKey#auto_rotate}
        :param cert_data_base64: PEM Certificate in a Base64 format. Used for updating RSA keys' certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#cert_data_base64 DfcKey#cert_data_base64}
        :param certificate_common_name: Common name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_common_name DfcKey#certificate_common_name}
        :param certificate_country: Country name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_country DfcKey#certificate_country}
        :param certificate_format: The format of the returned certificate [pem/der]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_format DfcKey#certificate_format}
        :param certificate_locality: Locality for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_locality DfcKey#certificate_locality}
        :param certificate_organization: Organization name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_organization DfcKey#certificate_organization}
        :param certificate_province: Province name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_province DfcKey#certificate_province}
        :param certificate_ttl: TTL in days for the generated certificate. Required only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_ttl DfcKey#certificate_ttl}
        :param conf_file_data: The csr config data in base64 encoding. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#conf_file_data DfcKey#conf_file_data}
        :param customer_frg_id: The customer fragment ID that will be used to create the DFC key (if empty, the key will be created independently of a customer fragment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#customer_frg_id DfcKey#customer_frg_id}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#delete_protection DfcKey#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#description DfcKey#description}
        :param expiration_event_in: How many days before the expiration of the certificate would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#expiration_event_in DfcKey#expiration_event_in}
        :param generate_self_signed_certificate: Whether to generate a self signed certificate with the key. If set, certificate-ttl must be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#generate_self_signed_certificate DfcKey#generate_self_signed_certificate}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#id DfcKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rotation_event_in: How many days before the rotation of the item would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#rotation_event_in DfcKey#rotation_event_in}
        :param rotation_interval: The number of days to wait between every automatic rotation (7-365). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#rotation_interval DfcKey#rotation_interval}
        :param split_level: The number of fragments that the item will be split into (not includes customer fragment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#split_level DfcKey#split_level}
        :param tags: List of the tags attached to this DFC key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#tags DfcKey#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a9e4f3b470c94174034b8bb79c39c82a2de375beb245047a52b51fc8fe8726d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DfcKeyConfig(
            alg=alg,
            name=name,
            auto_rotate=auto_rotate,
            cert_data_base64=cert_data_base64,
            certificate_common_name=certificate_common_name,
            certificate_country=certificate_country,
            certificate_format=certificate_format,
            certificate_locality=certificate_locality,
            certificate_organization=certificate_organization,
            certificate_province=certificate_province,
            certificate_ttl=certificate_ttl,
            conf_file_data=conf_file_data,
            customer_frg_id=customer_frg_id,
            delete_protection=delete_protection,
            description=description,
            expiration_event_in=expiration_event_in,
            generate_self_signed_certificate=generate_self_signed_certificate,
            id=id,
            rotation_event_in=rotation_event_in,
            rotation_interval=rotation_interval,
            split_level=split_level,
            tags=tags,
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
        '''Generates CDKTF code for importing a DfcKey resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DfcKey to import.
        :param import_from_id: The id of the existing DfcKey that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DfcKey to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1d6430cc781e518debcfedb78fbdaffca48475d1a9898e345d2b1f4efb22695)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAutoRotate")
    def reset_auto_rotate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRotate", []))

    @jsii.member(jsii_name="resetCertDataBase64")
    def reset_cert_data_base64(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertDataBase64", []))

    @jsii.member(jsii_name="resetCertificateCommonName")
    def reset_certificate_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateCommonName", []))

    @jsii.member(jsii_name="resetCertificateCountry")
    def reset_certificate_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateCountry", []))

    @jsii.member(jsii_name="resetCertificateFormat")
    def reset_certificate_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateFormat", []))

    @jsii.member(jsii_name="resetCertificateLocality")
    def reset_certificate_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateLocality", []))

    @jsii.member(jsii_name="resetCertificateOrganization")
    def reset_certificate_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateOrganization", []))

    @jsii.member(jsii_name="resetCertificateProvince")
    def reset_certificate_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateProvince", []))

    @jsii.member(jsii_name="resetCertificateTtl")
    def reset_certificate_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateTtl", []))

    @jsii.member(jsii_name="resetConfFileData")
    def reset_conf_file_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfFileData", []))

    @jsii.member(jsii_name="resetCustomerFrgId")
    def reset_customer_frg_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerFrgId", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExpirationEventIn")
    def reset_expiration_event_in(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationEventIn", []))

    @jsii.member(jsii_name="resetGenerateSelfSignedCertificate")
    def reset_generate_self_signed_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenerateSelfSignedCertificate", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRotationEventIn")
    def reset_rotation_event_in(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationEventIn", []))

    @jsii.member(jsii_name="resetRotationInterval")
    def reset_rotation_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationInterval", []))

    @jsii.member(jsii_name="resetSplitLevel")
    def reset_split_level(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSplitLevel", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="algInput")
    def alg_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRotateInput")
    def auto_rotate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autoRotateInput"))

    @builtins.property
    @jsii.member(jsii_name="certDataBase64Input")
    def cert_data_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certDataBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="certificateCommonNameInput")
    def certificate_common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateCommonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateCountryInput")
    def certificate_country_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateCountryInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateFormatInput")
    def certificate_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateLocalityInput")
    def certificate_locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateLocalityInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateOrganizationInput")
    def certificate_organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateProvinceInput")
    def certificate_province_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateProvinceInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateTtlInput")
    def certificate_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "certificateTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="confFileDataInput")
    def conf_file_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "confFileDataInput"))

    @builtins.property
    @jsii.member(jsii_name="customerFrgIdInput")
    def customer_frg_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerFrgIdInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationEventInInput")
    def expiration_event_in_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "expirationEventInInput"))

    @builtins.property
    @jsii.member(jsii_name="generateSelfSignedCertificateInput")
    def generate_self_signed_certificate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "generateSelfSignedCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationEventInInput")
    def rotation_event_in_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rotationEventInInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationIntervalInput")
    def rotation_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="splitLevelInput")
    def split_level_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "splitLevelInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="alg")
    def alg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alg"))

    @alg.setter
    def alg(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a07f014386564b9024e5de6c7f21ed672820d20eaecabf5526c45a9bbc82cdfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alg", value)

    @builtins.property
    @jsii.member(jsii_name="autoRotate")
    def auto_rotate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoRotate"))

    @auto_rotate.setter
    def auto_rotate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21e7dc80aa9a4bc8d3eb5311474ea5c983da30c87dc44fc0f03c502b26d6c155)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRotate", value)

    @builtins.property
    @jsii.member(jsii_name="certDataBase64")
    def cert_data_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certDataBase64"))

    @cert_data_base64.setter
    def cert_data_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1ba574302ae83e1124429e348e3ae8fa0554b18d5408f8bf083e56b0a2152cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certDataBase64", value)

    @builtins.property
    @jsii.member(jsii_name="certificateCommonName")
    def certificate_common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateCommonName"))

    @certificate_common_name.setter
    def certificate_common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__024f8af0b8a6cf2fbe15b479abffcb4f9b612d6a9b77ec0c370862f708c1b3e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateCommonName", value)

    @builtins.property
    @jsii.member(jsii_name="certificateCountry")
    def certificate_country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateCountry"))

    @certificate_country.setter
    def certificate_country(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff431e68b0017b03d8473a2ec2a6ccb4fc0104e1e4fbeb8b80a711f591ebe036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateCountry", value)

    @builtins.property
    @jsii.member(jsii_name="certificateFormat")
    def certificate_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateFormat"))

    @certificate_format.setter
    def certificate_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38f45f4d165a0eeb522a2ac3be58529240e834ad61cc0a2bd946e5ede88a8fba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateFormat", value)

    @builtins.property
    @jsii.member(jsii_name="certificateLocality")
    def certificate_locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateLocality"))

    @certificate_locality.setter
    def certificate_locality(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70e970df24d2617a558c7e32114598615d7d3ea43fa82104a77572bb700285f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateLocality", value)

    @builtins.property
    @jsii.member(jsii_name="certificateOrganization")
    def certificate_organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateOrganization"))

    @certificate_organization.setter
    def certificate_organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa20dd0902eed269407822d46af5a9720b99ac2923bcd79902b3b7142ef1339b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateOrganization", value)

    @builtins.property
    @jsii.member(jsii_name="certificateProvince")
    def certificate_province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateProvince"))

    @certificate_province.setter
    def certificate_province(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c86572290017386ec5f21527e63e98eb74e2183bc89c1307065aa04ea6c81241)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateProvince", value)

    @builtins.property
    @jsii.member(jsii_name="certificateTtl")
    def certificate_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "certificateTtl"))

    @certificate_ttl.setter
    def certificate_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26361fe19c4bc50bcd46895a2736888d49071fab5b9c8ac359c987a1fdeca0ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateTtl", value)

    @builtins.property
    @jsii.member(jsii_name="confFileData")
    def conf_file_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "confFileData"))

    @conf_file_data.setter
    def conf_file_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8acf18c1b7b25615ce6b0e0dee15b8813ae2d3900194840aa4a994376365d6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confFileData", value)

    @builtins.property
    @jsii.member(jsii_name="customerFrgId")
    def customer_frg_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerFrgId"))

    @customer_frg_id.setter
    def customer_frg_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__652f890f1c3cdf92c264e0bc7f8f1c83767ed33a9862d2159f8bcfe58de95397)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customerFrgId", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ebeddc9c34a5b0aed37b38d72fa36743551ce5ed3098e10c3fb614516ecab69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fdc2a6223234c8e4bf551941c7f1ab0241eb12a93ae9b27e918b6da96942958)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="expirationEventIn")
    def expiration_event_in(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "expirationEventIn"))

    @expiration_event_in.setter
    def expiration_event_in(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f22cd455cb7cc2ceb82e1c9335c5ae2a6d92fa7edc4881698e2025b5e0b865b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationEventIn", value)

    @builtins.property
    @jsii.member(jsii_name="generateSelfSignedCertificate")
    def generate_self_signed_certificate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "generateSelfSignedCertificate"))

    @generate_self_signed_certificate.setter
    def generate_self_signed_certificate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__469b89b2f46618de20fa3bb096ed68261a6b3d9fab9e61d65ca3f105069f708e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generateSelfSignedCertificate", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ae08490aba4d5dde4f2c1885ab3a00c6c7a3c75418e0cb3f7cf0cbb5795e9cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dead856b5858dadeda68d3ccc366cb10614790da7a202a3cdafdefce904ab97c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="rotationEventIn")
    def rotation_event_in(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "rotationEventIn"))

    @rotation_event_in.setter
    def rotation_event_in(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f79e644f14835a28814ee5e6ce7395067d297095ab3c43c6fa6e439f1bd5244)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationEventIn", value)

    @builtins.property
    @jsii.member(jsii_name="rotationInterval")
    def rotation_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationInterval"))

    @rotation_interval.setter
    def rotation_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc3d02d8b798feebb284588f549a7ac30b477140380725dcec178813c5b6aadc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationInterval", value)

    @builtins.property
    @jsii.member(jsii_name="splitLevel")
    def split_level(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "splitLevel"))

    @split_level.setter
    def split_level(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f4fa5900d302a53e2ec2b3c02487721de9fcff81f9179895619f7cf6d0dbbc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "splitLevel", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6411f728be63a777397f2edfa45d8cdc2b24cf7007488ebdba545adf7ec77da1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="akeyless.dfcKey.DfcKeyConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "alg": "alg",
        "name": "name",
        "auto_rotate": "autoRotate",
        "cert_data_base64": "certDataBase64",
        "certificate_common_name": "certificateCommonName",
        "certificate_country": "certificateCountry",
        "certificate_format": "certificateFormat",
        "certificate_locality": "certificateLocality",
        "certificate_organization": "certificateOrganization",
        "certificate_province": "certificateProvince",
        "certificate_ttl": "certificateTtl",
        "conf_file_data": "confFileData",
        "customer_frg_id": "customerFrgId",
        "delete_protection": "deleteProtection",
        "description": "description",
        "expiration_event_in": "expirationEventIn",
        "generate_self_signed_certificate": "generateSelfSignedCertificate",
        "id": "id",
        "rotation_event_in": "rotationEventIn",
        "rotation_interval": "rotationInterval",
        "split_level": "splitLevel",
        "tags": "tags",
    },
)
class DfcKeyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        alg: builtins.str,
        name: builtins.str,
        auto_rotate: typing.Optional[builtins.str] = None,
        cert_data_base64: typing.Optional[builtins.str] = None,
        certificate_common_name: typing.Optional[builtins.str] = None,
        certificate_country: typing.Optional[builtins.str] = None,
        certificate_format: typing.Optional[builtins.str] = None,
        certificate_locality: typing.Optional[builtins.str] = None,
        certificate_organization: typing.Optional[builtins.str] = None,
        certificate_province: typing.Optional[builtins.str] = None,
        certificate_ttl: typing.Optional[jsii.Number] = None,
        conf_file_data: typing.Optional[builtins.str] = None,
        customer_frg_id: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
        split_level: typing.Optional[jsii.Number] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param alg: DFCKey type; options: [AES128GCM, AES256GCM, AES128SIV, AES256SIV, AES128CBC, AES256CBC, RSA1024, RSA2048, RSA3072, RSA4096]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#alg DfcKey#alg}
        :param name: DFCKey name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#name DfcKey#name}
        :param auto_rotate: Whether to automatically rotate every rotation_interval days, or disable existing automatic rotation [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#auto_rotate DfcKey#auto_rotate}
        :param cert_data_base64: PEM Certificate in a Base64 format. Used for updating RSA keys' certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#cert_data_base64 DfcKey#cert_data_base64}
        :param certificate_common_name: Common name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_common_name DfcKey#certificate_common_name}
        :param certificate_country: Country name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_country DfcKey#certificate_country}
        :param certificate_format: The format of the returned certificate [pem/der]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_format DfcKey#certificate_format}
        :param certificate_locality: Locality for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_locality DfcKey#certificate_locality}
        :param certificate_organization: Organization name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_organization DfcKey#certificate_organization}
        :param certificate_province: Province name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_province DfcKey#certificate_province}
        :param certificate_ttl: TTL in days for the generated certificate. Required only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_ttl DfcKey#certificate_ttl}
        :param conf_file_data: The csr config data in base64 encoding. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#conf_file_data DfcKey#conf_file_data}
        :param customer_frg_id: The customer fragment ID that will be used to create the DFC key (if empty, the key will be created independently of a customer fragment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#customer_frg_id DfcKey#customer_frg_id}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#delete_protection DfcKey#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#description DfcKey#description}
        :param expiration_event_in: How many days before the expiration of the certificate would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#expiration_event_in DfcKey#expiration_event_in}
        :param generate_self_signed_certificate: Whether to generate a self signed certificate with the key. If set, certificate-ttl must be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#generate_self_signed_certificate DfcKey#generate_self_signed_certificate}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#id DfcKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rotation_event_in: How many days before the rotation of the item would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#rotation_event_in DfcKey#rotation_event_in}
        :param rotation_interval: The number of days to wait between every automatic rotation (7-365). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#rotation_interval DfcKey#rotation_interval}
        :param split_level: The number of fragments that the item will be split into (not includes customer fragment). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#split_level DfcKey#split_level}
        :param tags: List of the tags attached to this DFC key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#tags DfcKey#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ceea1f6298e36670bd183510c050ea6f3a2d66ce97f09653f35b7b0e9d6760d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument alg", value=alg, expected_type=type_hints["alg"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument auto_rotate", value=auto_rotate, expected_type=type_hints["auto_rotate"])
            check_type(argname="argument cert_data_base64", value=cert_data_base64, expected_type=type_hints["cert_data_base64"])
            check_type(argname="argument certificate_common_name", value=certificate_common_name, expected_type=type_hints["certificate_common_name"])
            check_type(argname="argument certificate_country", value=certificate_country, expected_type=type_hints["certificate_country"])
            check_type(argname="argument certificate_format", value=certificate_format, expected_type=type_hints["certificate_format"])
            check_type(argname="argument certificate_locality", value=certificate_locality, expected_type=type_hints["certificate_locality"])
            check_type(argname="argument certificate_organization", value=certificate_organization, expected_type=type_hints["certificate_organization"])
            check_type(argname="argument certificate_province", value=certificate_province, expected_type=type_hints["certificate_province"])
            check_type(argname="argument certificate_ttl", value=certificate_ttl, expected_type=type_hints["certificate_ttl"])
            check_type(argname="argument conf_file_data", value=conf_file_data, expected_type=type_hints["conf_file_data"])
            check_type(argname="argument customer_frg_id", value=customer_frg_id, expected_type=type_hints["customer_frg_id"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument expiration_event_in", value=expiration_event_in, expected_type=type_hints["expiration_event_in"])
            check_type(argname="argument generate_self_signed_certificate", value=generate_self_signed_certificate, expected_type=type_hints["generate_self_signed_certificate"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rotation_event_in", value=rotation_event_in, expected_type=type_hints["rotation_event_in"])
            check_type(argname="argument rotation_interval", value=rotation_interval, expected_type=type_hints["rotation_interval"])
            check_type(argname="argument split_level", value=split_level, expected_type=type_hints["split_level"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "alg": alg,
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
        if auto_rotate is not None:
            self._values["auto_rotate"] = auto_rotate
        if cert_data_base64 is not None:
            self._values["cert_data_base64"] = cert_data_base64
        if certificate_common_name is not None:
            self._values["certificate_common_name"] = certificate_common_name
        if certificate_country is not None:
            self._values["certificate_country"] = certificate_country
        if certificate_format is not None:
            self._values["certificate_format"] = certificate_format
        if certificate_locality is not None:
            self._values["certificate_locality"] = certificate_locality
        if certificate_organization is not None:
            self._values["certificate_organization"] = certificate_organization
        if certificate_province is not None:
            self._values["certificate_province"] = certificate_province
        if certificate_ttl is not None:
            self._values["certificate_ttl"] = certificate_ttl
        if conf_file_data is not None:
            self._values["conf_file_data"] = conf_file_data
        if customer_frg_id is not None:
            self._values["customer_frg_id"] = customer_frg_id
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if expiration_event_in is not None:
            self._values["expiration_event_in"] = expiration_event_in
        if generate_self_signed_certificate is not None:
            self._values["generate_self_signed_certificate"] = generate_self_signed_certificate
        if id is not None:
            self._values["id"] = id
        if rotation_event_in is not None:
            self._values["rotation_event_in"] = rotation_event_in
        if rotation_interval is not None:
            self._values["rotation_interval"] = rotation_interval
        if split_level is not None:
            self._values["split_level"] = split_level
        if tags is not None:
            self._values["tags"] = tags

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
    def alg(self) -> builtins.str:
        '''DFCKey type; options: [AES128GCM, AES256GCM, AES128SIV, AES256SIV, AES128CBC, AES256CBC, RSA1024, RSA2048, RSA3072, RSA4096].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#alg DfcKey#alg}
        '''
        result = self._values.get("alg")
        assert result is not None, "Required property 'alg' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''DFCKey name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#name DfcKey#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_rotate(self) -> typing.Optional[builtins.str]:
        '''Whether to automatically rotate every rotation_interval days, or disable existing automatic rotation [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#auto_rotate DfcKey#auto_rotate}
        '''
        result = self._values.get("auto_rotate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_data_base64(self) -> typing.Optional[builtins.str]:
        '''PEM Certificate in a Base64 format. Used for updating RSA keys' certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#cert_data_base64 DfcKey#cert_data_base64}
        '''
        result = self._values.get("cert_data_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_common_name(self) -> typing.Optional[builtins.str]:
        '''Common name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_common_name DfcKey#certificate_common_name}
        '''
        result = self._values.get("certificate_common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_country(self) -> typing.Optional[builtins.str]:
        '''Country name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_country DfcKey#certificate_country}
        '''
        result = self._values.get("certificate_country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_format(self) -> typing.Optional[builtins.str]:
        '''The format of the returned certificate [pem/der].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_format DfcKey#certificate_format}
        '''
        result = self._values.get("certificate_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_locality(self) -> typing.Optional[builtins.str]:
        '''Locality for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_locality DfcKey#certificate_locality}
        '''
        result = self._values.get("certificate_locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_organization(self) -> typing.Optional[builtins.str]:
        '''Organization name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_organization DfcKey#certificate_organization}
        '''
        result = self._values.get("certificate_organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_province(self) -> typing.Optional[builtins.str]:
        '''Province name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_province DfcKey#certificate_province}
        '''
        result = self._values.get("certificate_province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_ttl(self) -> typing.Optional[jsii.Number]:
        '''TTL in days for the generated certificate. Required only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#certificate_ttl DfcKey#certificate_ttl}
        '''
        result = self._values.get("certificate_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def conf_file_data(self) -> typing.Optional[builtins.str]:
        '''The csr config data in base64 encoding.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#conf_file_data DfcKey#conf_file_data}
        '''
        result = self._values.get("conf_file_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def customer_frg_id(self) -> typing.Optional[builtins.str]:
        '''The customer fragment ID that will be used to create the DFC key (if empty, the key will be created independently of a customer fragment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#customer_frg_id DfcKey#customer_frg_id}
        '''
        result = self._values.get("customer_frg_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Protection from accidental deletion of this item, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#delete_protection DfcKey#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#description DfcKey#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expiration_event_in(self) -> typing.Optional[typing.List[builtins.str]]:
        '''How many days before the expiration of the certificate would you like to be notified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#expiration_event_in DfcKey#expiration_event_in}
        '''
        result = self._values.get("expiration_event_in")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def generate_self_signed_certificate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to generate a self signed certificate with the key. If set, certificate-ttl must be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#generate_self_signed_certificate DfcKey#generate_self_signed_certificate}
        '''
        result = self._values.get("generate_self_signed_certificate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#id DfcKey#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_event_in(self) -> typing.Optional[typing.List[builtins.str]]:
        '''How many days before the rotation of the item would you like to be notified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#rotation_event_in DfcKey#rotation_event_in}
        '''
        result = self._values.get("rotation_event_in")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def rotation_interval(self) -> typing.Optional[builtins.str]:
        '''The number of days to wait between every automatic rotation (7-365).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#rotation_interval DfcKey#rotation_interval}
        '''
        result = self._values.get("rotation_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def split_level(self) -> typing.Optional[jsii.Number]:
        '''The number of fragments that the item will be split into (not includes customer fragment).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#split_level DfcKey#split_level}
        '''
        result = self._values.get("split_level")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this DFC key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dfc_key#tags DfcKey#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DfcKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DfcKey",
    "DfcKeyConfig",
]

publication.publish()

def _typecheckingstub__1a9e4f3b470c94174034b8bb79c39c82a2de375beb245047a52b51fc8fe8726d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    alg: builtins.str,
    name: builtins.str,
    auto_rotate: typing.Optional[builtins.str] = None,
    cert_data_base64: typing.Optional[builtins.str] = None,
    certificate_common_name: typing.Optional[builtins.str] = None,
    certificate_country: typing.Optional[builtins.str] = None,
    certificate_format: typing.Optional[builtins.str] = None,
    certificate_locality: typing.Optional[builtins.str] = None,
    certificate_organization: typing.Optional[builtins.str] = None,
    certificate_province: typing.Optional[builtins.str] = None,
    certificate_ttl: typing.Optional[jsii.Number] = None,
    conf_file_data: typing.Optional[builtins.str] = None,
    customer_frg_id: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    split_level: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__b1d6430cc781e518debcfedb78fbdaffca48475d1a9898e345d2b1f4efb22695(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a07f014386564b9024e5de6c7f21ed672820d20eaecabf5526c45a9bbc82cdfb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21e7dc80aa9a4bc8d3eb5311474ea5c983da30c87dc44fc0f03c502b26d6c155(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1ba574302ae83e1124429e348e3ae8fa0554b18d5408f8bf083e56b0a2152cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__024f8af0b8a6cf2fbe15b479abffcb4f9b612d6a9b77ec0c370862f708c1b3e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff431e68b0017b03d8473a2ec2a6ccb4fc0104e1e4fbeb8b80a711f591ebe036(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38f45f4d165a0eeb522a2ac3be58529240e834ad61cc0a2bd946e5ede88a8fba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70e970df24d2617a558c7e32114598615d7d3ea43fa82104a77572bb700285f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa20dd0902eed269407822d46af5a9720b99ac2923bcd79902b3b7142ef1339b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c86572290017386ec5f21527e63e98eb74e2183bc89c1307065aa04ea6c81241(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26361fe19c4bc50bcd46895a2736888d49071fab5b9c8ac359c987a1fdeca0ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8acf18c1b7b25615ce6b0e0dee15b8813ae2d3900194840aa4a994376365d6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__652f890f1c3cdf92c264e0bc7f8f1c83767ed33a9862d2159f8bcfe58de95397(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ebeddc9c34a5b0aed37b38d72fa36743551ce5ed3098e10c3fb614516ecab69(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fdc2a6223234c8e4bf551941c7f1ab0241eb12a93ae9b27e918b6da96942958(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f22cd455cb7cc2ceb82e1c9335c5ae2a6d92fa7edc4881698e2025b5e0b865b5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469b89b2f46618de20fa3bb096ed68261a6b3d9fab9e61d65ca3f105069f708e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ae08490aba4d5dde4f2c1885ab3a00c6c7a3c75418e0cb3f7cf0cbb5795e9cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dead856b5858dadeda68d3ccc366cb10614790da7a202a3cdafdefce904ab97c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f79e644f14835a28814ee5e6ce7395067d297095ab3c43c6fa6e439f1bd5244(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc3d02d8b798feebb284588f549a7ac30b477140380725dcec178813c5b6aadc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f4fa5900d302a53e2ec2b3c02487721de9fcff81f9179895619f7cf6d0dbbc4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6411f728be63a777397f2edfa45d8cdc2b24cf7007488ebdba545adf7ec77da1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ceea1f6298e36670bd183510c050ea6f3a2d66ce97f09653f35b7b0e9d6760d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    alg: builtins.str,
    name: builtins.str,
    auto_rotate: typing.Optional[builtins.str] = None,
    cert_data_base64: typing.Optional[builtins.str] = None,
    certificate_common_name: typing.Optional[builtins.str] = None,
    certificate_country: typing.Optional[builtins.str] = None,
    certificate_format: typing.Optional[builtins.str] = None,
    certificate_locality: typing.Optional[builtins.str] = None,
    certificate_organization: typing.Optional[builtins.str] = None,
    certificate_province: typing.Optional[builtins.str] = None,
    certificate_ttl: typing.Optional[jsii.Number] = None,
    conf_file_data: typing.Optional[builtins.str] = None,
    customer_frg_id: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    split_level: typing.Optional[jsii.Number] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
