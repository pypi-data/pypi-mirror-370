'''
# `akeyless_classic_key`

Refer to the Terraform Registry for docs: [`akeyless_classic_key`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key).
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


class ClassicKey(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.classicKey.ClassicKey",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key akeyless_classic_key}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        alg: builtins.str,
        name: builtins.str,
        auto_rotate: typing.Optional[builtins.str] = None,
        cert_file_data: typing.Optional[builtins.str] = None,
        certificate_common_name: typing.Optional[builtins.str] = None,
        certificate_country: typing.Optional[builtins.str] = None,
        certificate_format: typing.Optional[builtins.str] = None,
        certificate_locality: typing.Optional[builtins.str] = None,
        certificate_organization: typing.Optional[builtins.str] = None,
        certificate_province: typing.Optional[builtins.str] = None,
        certificate_ttl: typing.Optional[jsii.Number] = None,
        conf_file_data: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gpg_alg: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_data: typing.Optional[builtins.str] = None,
        protection_key_name: typing.Optional[builtins.str] = None,
        rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key akeyless_classic_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alg: Key type; options: [AES128GCM, AES256GCM, AES128SIV, AES256SIV, AES128CBC, AES256CBC, RSA1024, RSA2048, RSA3072, RSA4096, EC256, EC384, GPG]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#alg ClassicKey#alg}
        :param name: Classic key name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#name ClassicKey#name}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#auto_rotate ClassicKey#auto_rotate}
        :param cert_file_data: PEM Certificate in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#cert_file_data ClassicKey#cert_file_data}
        :param certificate_common_name: Common name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_common_name ClassicKey#certificate_common_name}
        :param certificate_country: Country name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_country ClassicKey#certificate_country}
        :param certificate_format: The format of the returned certificate [pem/der]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_format ClassicKey#certificate_format}
        :param certificate_locality: Locality for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_locality ClassicKey#certificate_locality}
        :param certificate_organization: Organization name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_organization ClassicKey#certificate_organization}
        :param certificate_province: Province name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_province ClassicKey#certificate_province}
        :param certificate_ttl: TTL in days for the generated certificate. Required only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_ttl ClassicKey#certificate_ttl}
        :param conf_file_data: The csr config data in base64 encoding. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#conf_file_data ClassicKey#conf_file_data}
        :param delete_protection: Protection from accidental deletion of this object, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#delete_protection ClassicKey#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#description ClassicKey#description}
        :param expiration_event_in: How many days before the expiration of the certificate would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#expiration_event_in ClassicKey#expiration_event_in}
        :param generate_self_signed_certificate: Whether to generate a self signed certificate with the key. If set, certificate_ttl must be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#generate_self_signed_certificate ClassicKey#generate_self_signed_certificate}
        :param gpg_alg: gpg alg: Relevant only if GPG key type selected; options: [RSA1024, RSA2048, RSA3072, RSA4096, Ed25519]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#gpg_alg ClassicKey#gpg_alg}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#id ClassicKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_data: Base64-encoded classic key value provided by user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#key_data ClassicKey#key_data}
        :param protection_key_name: The name of the key that protects the classic key value (if empty, the account default key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#protection_key_name ClassicKey#protection_key_name}
        :param rotation_event_in: How many days before the rotation of the item would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#rotation_event_in ClassicKey#rotation_event_in}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#rotation_interval ClassicKey#rotation_interval}
        :param tags: List of the tags attached to this key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#tags ClassicKey#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1024c50acd73e06dea07c1994d88da9cd04044f93f048cc10ada713bc8beefcd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ClassicKeyConfig(
            alg=alg,
            name=name,
            auto_rotate=auto_rotate,
            cert_file_data=cert_file_data,
            certificate_common_name=certificate_common_name,
            certificate_country=certificate_country,
            certificate_format=certificate_format,
            certificate_locality=certificate_locality,
            certificate_organization=certificate_organization,
            certificate_province=certificate_province,
            certificate_ttl=certificate_ttl,
            conf_file_data=conf_file_data,
            delete_protection=delete_protection,
            description=description,
            expiration_event_in=expiration_event_in,
            generate_self_signed_certificate=generate_self_signed_certificate,
            gpg_alg=gpg_alg,
            id=id,
            key_data=key_data,
            protection_key_name=protection_key_name,
            rotation_event_in=rotation_event_in,
            rotation_interval=rotation_interval,
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
        '''Generates CDKTF code for importing a ClassicKey resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ClassicKey to import.
        :param import_from_id: The id of the existing ClassicKey that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ClassicKey to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e31388eda7b20e635eff73f3c713f1476a3230bef076be1681ae0b065b3e713)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAutoRotate")
    def reset_auto_rotate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRotate", []))

    @jsii.member(jsii_name="resetCertFileData")
    def reset_cert_file_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertFileData", []))

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

    @jsii.member(jsii_name="resetGpgAlg")
    def reset_gpg_alg(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGpgAlg", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyData")
    def reset_key_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyData", []))

    @jsii.member(jsii_name="resetProtectionKeyName")
    def reset_protection_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtectionKeyName", []))

    @jsii.member(jsii_name="resetRotationEventIn")
    def reset_rotation_event_in(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationEventIn", []))

    @jsii.member(jsii_name="resetRotationInterval")
    def reset_rotation_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRotationInterval", []))

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
    @jsii.member(jsii_name="certFileDataInput")
    def cert_file_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certFileDataInput"))

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
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

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
    @jsii.member(jsii_name="gpgAlgInput")
    def gpg_alg_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gpgAlgInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyDataInput")
    def key_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyDataInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="protectionKeyNameInput")
    def protection_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protectionKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationEventInInput")
    def rotation_event_in_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rotationEventInInput"))

    @builtins.property
    @jsii.member(jsii_name="rotationIntervalInput")
    def rotation_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rotationIntervalInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__69b05bfaf1dd9a159a610bd050c53879ab0eb2b24f41cc14cdd1e4e45d1e454c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alg", value)

    @builtins.property
    @jsii.member(jsii_name="autoRotate")
    def auto_rotate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autoRotate"))

    @auto_rotate.setter
    def auto_rotate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d029ab0943bd6ba2c62b969c0ed103f6c5eb2bc7d5aea516fd58ac7c4c1c1df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRotate", value)

    @builtins.property
    @jsii.member(jsii_name="certFileData")
    def cert_file_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certFileData"))

    @cert_file_data.setter
    def cert_file_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dd35c7faa6dd5550f702dc7cd8e23fa523296ff7d0f5cf54988adad0b0caead)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certFileData", value)

    @builtins.property
    @jsii.member(jsii_name="certificateCommonName")
    def certificate_common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateCommonName"))

    @certificate_common_name.setter
    def certificate_common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__219545d59b9a1573e186fa249bca211cb25df5dc4f79fde93ce16404070842a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateCommonName", value)

    @builtins.property
    @jsii.member(jsii_name="certificateCountry")
    def certificate_country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateCountry"))

    @certificate_country.setter
    def certificate_country(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00d991194c3937a5c302e2f71a291dbee37c2fab5841f86205f97bfe07ad1265)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateCountry", value)

    @builtins.property
    @jsii.member(jsii_name="certificateFormat")
    def certificate_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateFormat"))

    @certificate_format.setter
    def certificate_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a94ed3546f2e119fb585ac6d23ef60a1d669b289c92f7a3e22301cb04178dfb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateFormat", value)

    @builtins.property
    @jsii.member(jsii_name="certificateLocality")
    def certificate_locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateLocality"))

    @certificate_locality.setter
    def certificate_locality(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__287613369e3872522f0d844fd1cb5eb53a753e881a56af42e241ec9ad593ec44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateLocality", value)

    @builtins.property
    @jsii.member(jsii_name="certificateOrganization")
    def certificate_organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateOrganization"))

    @certificate_organization.setter
    def certificate_organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a261d4acaf2d4acd811f097f636fd6858f1d39b9fbd046868cb9377dae7d85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateOrganization", value)

    @builtins.property
    @jsii.member(jsii_name="certificateProvince")
    def certificate_province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateProvince"))

    @certificate_province.setter
    def certificate_province(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8405c1417d335ddcdfc75396b015d8aa8f35c94f3830586a1bba32356971f2d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateProvince", value)

    @builtins.property
    @jsii.member(jsii_name="certificateTtl")
    def certificate_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "certificateTtl"))

    @certificate_ttl.setter
    def certificate_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c06f2da140a7e9cd8e041d635c454ec8ed14252e39622db95ee7e4cf2e129ef1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateTtl", value)

    @builtins.property
    @jsii.member(jsii_name="confFileData")
    def conf_file_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "confFileData"))

    @conf_file_data.setter
    def conf_file_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d01382802ef73ab2fb95f2907ccc9a391ef8c37c8c5ff552f4e5ab010a2015f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "confFileData", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33fd1a86bb263bd11f96893dec1107fc0a878ad6a71fab7491c0412dd8ab9d6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c0979586069a9fdd103c32cf52736ae86a001b0b26b4faad59fe9d8662d7b33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="expirationEventIn")
    def expiration_event_in(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "expirationEventIn"))

    @expiration_event_in.setter
    def expiration_event_in(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__703f39d3c9e03037e1c016684bbe0db29aeeb6cce79272c848c5c231e24fafb0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a927323c0d3190e4f6233960a925962a48a03b1e61b22b93ba50960749c843f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generateSelfSignedCertificate", value)

    @builtins.property
    @jsii.member(jsii_name="gpgAlg")
    def gpg_alg(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gpgAlg"))

    @gpg_alg.setter
    def gpg_alg(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2c75fa9b9c2dfbbd184500a24785791573f26d59b00cdd460f0ee0fcbb53c11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gpgAlg", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7004123efc760422dfe12ad0de7aeb1bbb901b9492cbc96b1e26ce1fe1ed0af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="keyData")
    def key_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyData"))

    @key_data.setter
    def key_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33cbe612d41bc1b1e39d1a5f01044fb24ab026ecd5976569b4e4783d4b724036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyData", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__686d72f7b413569ce7355edc601a9fd1e5772475ad737d47b6f4da00cac28472)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="protectionKeyName")
    def protection_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protectionKeyName"))

    @protection_key_name.setter
    def protection_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f282ef72ec02ffdc5240508d461c3b5a05c3ba853e1ecf235de92505ef8197f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protectionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="rotationEventIn")
    def rotation_event_in(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "rotationEventIn"))

    @rotation_event_in.setter
    def rotation_event_in(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c74a062945e6d69c34718eca94d893e302e424bbc97167868a6b21dbe67e80a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationEventIn", value)

    @builtins.property
    @jsii.member(jsii_name="rotationInterval")
    def rotation_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rotationInterval"))

    @rotation_interval.setter
    def rotation_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10e29a1ff81803228c6b079126cddfe8ce49251433b0499f87226308b17b5a77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rotationInterval", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__972de7623e6466b02e32d4a29d8da855c2707beefb2cbf56af4efcb765e9c137)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)


@jsii.data_type(
    jsii_type="akeyless.classicKey.ClassicKeyConfig",
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
        "cert_file_data": "certFileData",
        "certificate_common_name": "certificateCommonName",
        "certificate_country": "certificateCountry",
        "certificate_format": "certificateFormat",
        "certificate_locality": "certificateLocality",
        "certificate_organization": "certificateOrganization",
        "certificate_province": "certificateProvince",
        "certificate_ttl": "certificateTtl",
        "conf_file_data": "confFileData",
        "delete_protection": "deleteProtection",
        "description": "description",
        "expiration_event_in": "expirationEventIn",
        "generate_self_signed_certificate": "generateSelfSignedCertificate",
        "gpg_alg": "gpgAlg",
        "id": "id",
        "key_data": "keyData",
        "protection_key_name": "protectionKeyName",
        "rotation_event_in": "rotationEventIn",
        "rotation_interval": "rotationInterval",
        "tags": "tags",
    },
)
class ClassicKeyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cert_file_data: typing.Optional[builtins.str] = None,
        certificate_common_name: typing.Optional[builtins.str] = None,
        certificate_country: typing.Optional[builtins.str] = None,
        certificate_format: typing.Optional[builtins.str] = None,
        certificate_locality: typing.Optional[builtins.str] = None,
        certificate_organization: typing.Optional[builtins.str] = None,
        certificate_province: typing.Optional[builtins.str] = None,
        certificate_ttl: typing.Optional[jsii.Number] = None,
        conf_file_data: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gpg_alg: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key_data: typing.Optional[builtins.str] = None,
        protection_key_name: typing.Optional[builtins.str] = None,
        rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        rotation_interval: typing.Optional[builtins.str] = None,
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
        :param alg: Key type; options: [AES128GCM, AES256GCM, AES128SIV, AES256SIV, AES128CBC, AES256CBC, RSA1024, RSA2048, RSA3072, RSA4096, EC256, EC384, GPG]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#alg ClassicKey#alg}
        :param name: Classic key name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#name ClassicKey#name}
        :param auto_rotate: Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#auto_rotate ClassicKey#auto_rotate}
        :param cert_file_data: PEM Certificate in a Base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#cert_file_data ClassicKey#cert_file_data}
        :param certificate_common_name: Common name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_common_name ClassicKey#certificate_common_name}
        :param certificate_country: Country name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_country ClassicKey#certificate_country}
        :param certificate_format: The format of the returned certificate [pem/der]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_format ClassicKey#certificate_format}
        :param certificate_locality: Locality for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_locality ClassicKey#certificate_locality}
        :param certificate_organization: Organization name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_organization ClassicKey#certificate_organization}
        :param certificate_province: Province name for the generated certificate. Relevant only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_province ClassicKey#certificate_province}
        :param certificate_ttl: TTL in days for the generated certificate. Required only for generate-self-signed-certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_ttl ClassicKey#certificate_ttl}
        :param conf_file_data: The csr config data in base64 encoding. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#conf_file_data ClassicKey#conf_file_data}
        :param delete_protection: Protection from accidental deletion of this object, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#delete_protection ClassicKey#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#description ClassicKey#description}
        :param expiration_event_in: How many days before the expiration of the certificate would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#expiration_event_in ClassicKey#expiration_event_in}
        :param generate_self_signed_certificate: Whether to generate a self signed certificate with the key. If set, certificate_ttl must be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#generate_self_signed_certificate ClassicKey#generate_self_signed_certificate}
        :param gpg_alg: gpg alg: Relevant only if GPG key type selected; options: [RSA1024, RSA2048, RSA3072, RSA4096, Ed25519]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#gpg_alg ClassicKey#gpg_alg}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#id ClassicKey#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_data: Base64-encoded classic key value provided by user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#key_data ClassicKey#key_data}
        :param protection_key_name: The name of the key that protects the classic key value (if empty, the account default key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#protection_key_name ClassicKey#protection_key_name}
        :param rotation_event_in: How many days before the rotation of the item would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#rotation_event_in ClassicKey#rotation_event_in}
        :param rotation_interval: The number of days to wait between every automatic rotation (1-365). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#rotation_interval ClassicKey#rotation_interval}
        :param tags: List of the tags attached to this key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#tags ClassicKey#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c8c1310031eb4b7260d8b0a713490fa2eaf10d3fe24868c504ff0adf55b6952)
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
            check_type(argname="argument cert_file_data", value=cert_file_data, expected_type=type_hints["cert_file_data"])
            check_type(argname="argument certificate_common_name", value=certificate_common_name, expected_type=type_hints["certificate_common_name"])
            check_type(argname="argument certificate_country", value=certificate_country, expected_type=type_hints["certificate_country"])
            check_type(argname="argument certificate_format", value=certificate_format, expected_type=type_hints["certificate_format"])
            check_type(argname="argument certificate_locality", value=certificate_locality, expected_type=type_hints["certificate_locality"])
            check_type(argname="argument certificate_organization", value=certificate_organization, expected_type=type_hints["certificate_organization"])
            check_type(argname="argument certificate_province", value=certificate_province, expected_type=type_hints["certificate_province"])
            check_type(argname="argument certificate_ttl", value=certificate_ttl, expected_type=type_hints["certificate_ttl"])
            check_type(argname="argument conf_file_data", value=conf_file_data, expected_type=type_hints["conf_file_data"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument expiration_event_in", value=expiration_event_in, expected_type=type_hints["expiration_event_in"])
            check_type(argname="argument generate_self_signed_certificate", value=generate_self_signed_certificate, expected_type=type_hints["generate_self_signed_certificate"])
            check_type(argname="argument gpg_alg", value=gpg_alg, expected_type=type_hints["gpg_alg"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_data", value=key_data, expected_type=type_hints["key_data"])
            check_type(argname="argument protection_key_name", value=protection_key_name, expected_type=type_hints["protection_key_name"])
            check_type(argname="argument rotation_event_in", value=rotation_event_in, expected_type=type_hints["rotation_event_in"])
            check_type(argname="argument rotation_interval", value=rotation_interval, expected_type=type_hints["rotation_interval"])
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
        if cert_file_data is not None:
            self._values["cert_file_data"] = cert_file_data
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
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if expiration_event_in is not None:
            self._values["expiration_event_in"] = expiration_event_in
        if generate_self_signed_certificate is not None:
            self._values["generate_self_signed_certificate"] = generate_self_signed_certificate
        if gpg_alg is not None:
            self._values["gpg_alg"] = gpg_alg
        if id is not None:
            self._values["id"] = id
        if key_data is not None:
            self._values["key_data"] = key_data
        if protection_key_name is not None:
            self._values["protection_key_name"] = protection_key_name
        if rotation_event_in is not None:
            self._values["rotation_event_in"] = rotation_event_in
        if rotation_interval is not None:
            self._values["rotation_interval"] = rotation_interval
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
        '''Key type; options: [AES128GCM, AES256GCM, AES128SIV, AES256SIV, AES128CBC, AES256CBC, RSA1024, RSA2048, RSA3072, RSA4096, EC256, EC384, GPG].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#alg ClassicKey#alg}
        '''
        result = self._values.get("alg")
        assert result is not None, "Required property 'alg' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Classic key name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#name ClassicKey#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_rotate(self) -> typing.Optional[builtins.str]:
        '''Whether to automatically rotate every --rotation-interval days, or disable existing automatic rotation [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#auto_rotate ClassicKey#auto_rotate}
        '''
        result = self._values.get("auto_rotate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_file_data(self) -> typing.Optional[builtins.str]:
        '''PEM Certificate in a Base64 format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#cert_file_data ClassicKey#cert_file_data}
        '''
        result = self._values.get("cert_file_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_common_name(self) -> typing.Optional[builtins.str]:
        '''Common name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_common_name ClassicKey#certificate_common_name}
        '''
        result = self._values.get("certificate_common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_country(self) -> typing.Optional[builtins.str]:
        '''Country name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_country ClassicKey#certificate_country}
        '''
        result = self._values.get("certificate_country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_format(self) -> typing.Optional[builtins.str]:
        '''The format of the returned certificate [pem/der].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_format ClassicKey#certificate_format}
        '''
        result = self._values.get("certificate_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_locality(self) -> typing.Optional[builtins.str]:
        '''Locality for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_locality ClassicKey#certificate_locality}
        '''
        result = self._values.get("certificate_locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_organization(self) -> typing.Optional[builtins.str]:
        '''Organization name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_organization ClassicKey#certificate_organization}
        '''
        result = self._values.get("certificate_organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_province(self) -> typing.Optional[builtins.str]:
        '''Province name for the generated certificate. Relevant only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_province ClassicKey#certificate_province}
        '''
        result = self._values.get("certificate_province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_ttl(self) -> typing.Optional[jsii.Number]:
        '''TTL in days for the generated certificate. Required only for generate-self-signed-certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#certificate_ttl ClassicKey#certificate_ttl}
        '''
        result = self._values.get("certificate_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def conf_file_data(self) -> typing.Optional[builtins.str]:
        '''The csr config data in base64 encoding.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#conf_file_data ClassicKey#conf_file_data}
        '''
        result = self._values.get("conf_file_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this object, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#delete_protection ClassicKey#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#description ClassicKey#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expiration_event_in(self) -> typing.Optional[typing.List[builtins.str]]:
        '''How many days before the expiration of the certificate would you like to be notified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#expiration_event_in ClassicKey#expiration_event_in}
        '''
        result = self._values.get("expiration_event_in")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def generate_self_signed_certificate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to generate a self signed certificate with the key. If set, certificate_ttl must be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#generate_self_signed_certificate ClassicKey#generate_self_signed_certificate}
        '''
        result = self._values.get("generate_self_signed_certificate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gpg_alg(self) -> typing.Optional[builtins.str]:
        '''gpg alg: Relevant only if GPG key type selected; options: [RSA1024, RSA2048, RSA3072, RSA4096, Ed25519].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#gpg_alg ClassicKey#gpg_alg}
        '''
        result = self._values.get("gpg_alg")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#id ClassicKey#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_data(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded classic key value provided by user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#key_data ClassicKey#key_data}
        '''
        result = self._values.get("key_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protection_key_name(self) -> typing.Optional[builtins.str]:
        '''The name of the key that protects the classic key value (if empty, the account default key will be used).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#protection_key_name ClassicKey#protection_key_name}
        '''
        result = self._values.get("protection_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rotation_event_in(self) -> typing.Optional[typing.List[builtins.str]]:
        '''How many days before the rotation of the item would you like to be notified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#rotation_event_in ClassicKey#rotation_event_in}
        '''
        result = self._values.get("rotation_event_in")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def rotation_interval(self) -> typing.Optional[builtins.str]:
        '''The number of days to wait between every automatic rotation (1-365).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#rotation_interval ClassicKey#rotation_interval}
        '''
        result = self._values.get("rotation_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/classic_key#tags ClassicKey#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClassicKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ClassicKey",
    "ClassicKeyConfig",
]

publication.publish()

def _typecheckingstub__1024c50acd73e06dea07c1994d88da9cd04044f93f048cc10ada713bc8beefcd(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    alg: builtins.str,
    name: builtins.str,
    auto_rotate: typing.Optional[builtins.str] = None,
    cert_file_data: typing.Optional[builtins.str] = None,
    certificate_common_name: typing.Optional[builtins.str] = None,
    certificate_country: typing.Optional[builtins.str] = None,
    certificate_format: typing.Optional[builtins.str] = None,
    certificate_locality: typing.Optional[builtins.str] = None,
    certificate_organization: typing.Optional[builtins.str] = None,
    certificate_province: typing.Optional[builtins.str] = None,
    certificate_ttl: typing.Optional[jsii.Number] = None,
    conf_file_data: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gpg_alg: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_data: typing.Optional[builtins.str] = None,
    protection_key_name: typing.Optional[builtins.str] = None,
    rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__7e31388eda7b20e635eff73f3c713f1476a3230bef076be1681ae0b065b3e713(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69b05bfaf1dd9a159a610bd050c53879ab0eb2b24f41cc14cdd1e4e45d1e454c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d029ab0943bd6ba2c62b969c0ed103f6c5eb2bc7d5aea516fd58ac7c4c1c1df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dd35c7faa6dd5550f702dc7cd8e23fa523296ff7d0f5cf54988adad0b0caead(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__219545d59b9a1573e186fa249bca211cb25df5dc4f79fde93ce16404070842a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00d991194c3937a5c302e2f71a291dbee37c2fab5841f86205f97bfe07ad1265(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a94ed3546f2e119fb585ac6d23ef60a1d669b289c92f7a3e22301cb04178dfb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__287613369e3872522f0d844fd1cb5eb53a753e881a56af42e241ec9ad593ec44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a261d4acaf2d4acd811f097f636fd6858f1d39b9fbd046868cb9377dae7d85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8405c1417d335ddcdfc75396b015d8aa8f35c94f3830586a1bba32356971f2d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c06f2da140a7e9cd8e041d635c454ec8ed14252e39622db95ee7e4cf2e129ef1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d01382802ef73ab2fb95f2907ccc9a391ef8c37c8c5ff552f4e5ab010a2015f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33fd1a86bb263bd11f96893dec1107fc0a878ad6a71fab7491c0412dd8ab9d6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c0979586069a9fdd103c32cf52736ae86a001b0b26b4faad59fe9d8662d7b33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__703f39d3c9e03037e1c016684bbe0db29aeeb6cce79272c848c5c231e24fafb0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a927323c0d3190e4f6233960a925962a48a03b1e61b22b93ba50960749c843f3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2c75fa9b9c2dfbbd184500a24785791573f26d59b00cdd460f0ee0fcbb53c11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7004123efc760422dfe12ad0de7aeb1bbb901b9492cbc96b1e26ce1fe1ed0af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33cbe612d41bc1b1e39d1a5f01044fb24ab026ecd5976569b4e4783d4b724036(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__686d72f7b413569ce7355edc601a9fd1e5772475ad737d47b6f4da00cac28472(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f282ef72ec02ffdc5240508d461c3b5a05c3ba853e1ecf235de92505ef8197f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c74a062945e6d69c34718eca94d893e302e424bbc97167868a6b21dbe67e80a0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10e29a1ff81803228c6b079126cddfe8ce49251433b0499f87226308b17b5a77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__972de7623e6466b02e32d4a29d8da855c2707beefb2cbf56af4efcb765e9c137(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c8c1310031eb4b7260d8b0a713490fa2eaf10d3fe24868c504ff0adf55b6952(
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
    cert_file_data: typing.Optional[builtins.str] = None,
    certificate_common_name: typing.Optional[builtins.str] = None,
    certificate_country: typing.Optional[builtins.str] = None,
    certificate_format: typing.Optional[builtins.str] = None,
    certificate_locality: typing.Optional[builtins.str] = None,
    certificate_organization: typing.Optional[builtins.str] = None,
    certificate_province: typing.Optional[builtins.str] = None,
    certificate_ttl: typing.Optional[jsii.Number] = None,
    conf_file_data: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    generate_self_signed_certificate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gpg_alg: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key_data: typing.Optional[builtins.str] = None,
    protection_key_name: typing.Optional[builtins.str] = None,
    rotation_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    rotation_interval: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
