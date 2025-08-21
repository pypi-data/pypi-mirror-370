'''
# `akeyless_pki_cert_issuer`

Refer to the Terraform Registry for docs: [`akeyless_pki_cert_issuer`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer).
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


class PkiCertIssuer(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.pkiCertIssuer.PkiCertIssuer",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer akeyless_pki_cert_issuer}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        ttl: builtins.str,
        allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_copy_ext_from_csr: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_domains: typing.Optional[builtins.str] = None,
        allowed_extra_extensions: typing.Optional[builtins.str] = None,
        allowed_uri_sans: typing.Optional[builtins.str] = None,
        allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ca_target: typing.Optional[builtins.str] = None,
        client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        country: typing.Optional[builtins.str] = None,
        create_private_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        create_public_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        critical_key_usage: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        destination_path: typing.Optional[builtins.str] = None,
        enable_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        gw_cluster_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        is_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        key_usage: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        not_enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        not_require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        organizational_units: typing.Optional[builtins.str] = None,
        organizations: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        protect_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        province: typing.Optional[builtins.str] = None,
        scheduled_renew: typing.Optional[jsii.Number] = None,
        server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        signer_key_name: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer akeyless_pki_cert_issuer} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: PKI certificate issuer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#name PkiCertIssuer#name}
        :param ttl: The maximum requested Time To Live for issued certificate by default in seconds, supported formats are s,m,h,d. In case of Public CA, this is based on the CA target's supported maximum TTLs Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#ttl PkiCertIssuer#ttl}
        :param allow_any_name: If set, clients can request certificates for any CN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_any_name PkiCertIssuer#allow_any_name}
        :param allow_copy_ext_from_csr: If set, will allow copying the extra extensions from the csr file (if given). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_copy_ext_from_csr PkiCertIssuer#allow_copy_ext_from_csr}
        :param allowed_domains: A list of the allowed domains that clients can request to be included in the certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_domains PkiCertIssuer#allowed_domains}
        :param allowed_extra_extensions: A json string that defines the allowed extra extensions for the pki cert issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_extra_extensions PkiCertIssuer#allowed_extra_extensions}
        :param allowed_uri_sans: A list of the allowed URIs that clients can request to be included in the certificate as part of the URI Subject Alternative Names (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_uri_sans PkiCertIssuer#allowed_uri_sans}
        :param allow_subdomains: If set, clients can request certificates for subdomains and wildcard subdomains of the allowed domains. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_subdomains PkiCertIssuer#allow_subdomains}
        :param auto_renew: Automatically renew certificates before expiration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#auto_renew PkiCertIssuer#auto_renew}
        :param ca_target: The name of an existing CA target to attach this PKI Certificate Issuer to, required in Public CA mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#ca_target PkiCertIssuer#ca_target}
        :param client_flag: If set, certificates will be flagged for client auth use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#client_flag PkiCertIssuer#client_flag}
        :param code_signing_flag: If set, certificates will be flagged for code signing use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#code_signing_flag PkiCertIssuer#code_signing_flag}
        :param country: A comma-separated list of countries that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#country PkiCertIssuer#country}
        :param create_private_crl: Set this to allow the issuer will expose a CRL endpoint in the Gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#create_private_crl PkiCertIssuer#create_private_crl}
        :param create_public_crl: Set this to allow the cert issuer will expose a public CRL endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#create_public_crl PkiCertIssuer#create_public_crl}
        :param critical_key_usage: Mark key usage as critical [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#critical_key_usage PkiCertIssuer#critical_key_usage}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#delete_protection PkiCertIssuer#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#description PkiCertIssuer#description}
        :param destination_path: A path in Akeyless which to save generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#destination_path PkiCertIssuer#destination_path}
        :param enable_acme: If set, the cert issuer will support the acme protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#enable_acme PkiCertIssuer#enable_acme}
        :param expiration_event_in: How many days before the expiration of the certificate would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#expiration_event_in PkiCertIssuer#expiration_event_in}
        :param gw_cluster_url: The GW cluster URL to issue the certificate from, required in Public CA mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#gw_cluster_url PkiCertIssuer#gw_cluster_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#id PkiCertIssuer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_ca: If set, the basic constraints extension will be added to certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#is_ca PkiCertIssuer#is_ca}
        :param key_usage: A comma-separated string or list of key usages. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#key_usage PkiCertIssuer#key_usage}
        :param locality: A comma-separated list of localities that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#locality PkiCertIssuer#locality}
        :param not_enforce_hostnames: If set, any names are allowed for CN and SANs in the certificate and not only a valid host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#not_enforce_hostnames PkiCertIssuer#not_enforce_hostnames}
        :param not_require_cn: If set, clients can request certificates without a CN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#not_require_cn PkiCertIssuer#not_require_cn}
        :param organizational_units: A comma-separated list of organizational units (OU) that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#organizational_units PkiCertIssuer#organizational_units}
        :param organizations: A comma-separated list of organizations (O) that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#organizations PkiCertIssuer#organizations}
        :param postal_code: A comma-separated list of postal codes that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#postal_code PkiCertIssuer#postal_code}
        :param protect_certificates: Whether to protect generated certificates from deletion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#protect_certificates PkiCertIssuer#protect_certificates}
        :param province: A comma-separated list of provinces that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#province PkiCertIssuer#province}
        :param scheduled_renew: Number of days before expiration to renew certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#scheduled_renew PkiCertIssuer#scheduled_renew}
        :param server_flag: If set, certificates will be flagged for server auth use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#server_flag PkiCertIssuer#server_flag}
        :param signer_key_name: A key to sign the certificate with, required in Private CA mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#signer_key_name PkiCertIssuer#signer_key_name}
        :param street_address: A comma-separated list of street addresses that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#street_address PkiCertIssuer#street_address}
        :param tags: List of the tags attached to this key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#tags PkiCertIssuer#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55917388f2ead456038a2b7821b39910718c10abf2a4f5d997e574d418fa26a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = PkiCertIssuerConfig(
            name=name,
            ttl=ttl,
            allow_any_name=allow_any_name,
            allow_copy_ext_from_csr=allow_copy_ext_from_csr,
            allowed_domains=allowed_domains,
            allowed_extra_extensions=allowed_extra_extensions,
            allowed_uri_sans=allowed_uri_sans,
            allow_subdomains=allow_subdomains,
            auto_renew=auto_renew,
            ca_target=ca_target,
            client_flag=client_flag,
            code_signing_flag=code_signing_flag,
            country=country,
            create_private_crl=create_private_crl,
            create_public_crl=create_public_crl,
            critical_key_usage=critical_key_usage,
            delete_protection=delete_protection,
            description=description,
            destination_path=destination_path,
            enable_acme=enable_acme,
            expiration_event_in=expiration_event_in,
            gw_cluster_url=gw_cluster_url,
            id=id,
            is_ca=is_ca,
            key_usage=key_usage,
            locality=locality,
            not_enforce_hostnames=not_enforce_hostnames,
            not_require_cn=not_require_cn,
            organizational_units=organizational_units,
            organizations=organizations,
            postal_code=postal_code,
            protect_certificates=protect_certificates,
            province=province,
            scheduled_renew=scheduled_renew,
            server_flag=server_flag,
            signer_key_name=signer_key_name,
            street_address=street_address,
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
        '''Generates CDKTF code for importing a PkiCertIssuer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PkiCertIssuer to import.
        :param import_from_id: The id of the existing PkiCertIssuer that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PkiCertIssuer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__434f722227df60f716d054150de2c9384cfcfff7d8141f0b9fd19321f3f3e6ec)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAllowAnyName")
    def reset_allow_any_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowAnyName", []))

    @jsii.member(jsii_name="resetAllowCopyExtFromCsr")
    def reset_allow_copy_ext_from_csr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowCopyExtFromCsr", []))

    @jsii.member(jsii_name="resetAllowedDomains")
    def reset_allowed_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedDomains", []))

    @jsii.member(jsii_name="resetAllowedExtraExtensions")
    def reset_allowed_extra_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedExtraExtensions", []))

    @jsii.member(jsii_name="resetAllowedUriSans")
    def reset_allowed_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedUriSans", []))

    @jsii.member(jsii_name="resetAllowSubdomains")
    def reset_allow_subdomains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowSubdomains", []))

    @jsii.member(jsii_name="resetAutoRenew")
    def reset_auto_renew(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoRenew", []))

    @jsii.member(jsii_name="resetCaTarget")
    def reset_ca_target(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaTarget", []))

    @jsii.member(jsii_name="resetClientFlag")
    def reset_client_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientFlag", []))

    @jsii.member(jsii_name="resetCodeSigningFlag")
    def reset_code_signing_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCodeSigningFlag", []))

    @jsii.member(jsii_name="resetCountry")
    def reset_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountry", []))

    @jsii.member(jsii_name="resetCreatePrivateCrl")
    def reset_create_private_crl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatePrivateCrl", []))

    @jsii.member(jsii_name="resetCreatePublicCrl")
    def reset_create_public_crl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatePublicCrl", []))

    @jsii.member(jsii_name="resetCriticalKeyUsage")
    def reset_critical_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCriticalKeyUsage", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDestinationPath")
    def reset_destination_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestinationPath", []))

    @jsii.member(jsii_name="resetEnableAcme")
    def reset_enable_acme(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableAcme", []))

    @jsii.member(jsii_name="resetExpirationEventIn")
    def reset_expiration_event_in(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationEventIn", []))

    @jsii.member(jsii_name="resetGwClusterUrl")
    def reset_gw_cluster_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGwClusterUrl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIsCa")
    def reset_is_ca(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCa", []))

    @jsii.member(jsii_name="resetKeyUsage")
    def reset_key_usage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyUsage", []))

    @jsii.member(jsii_name="resetLocality")
    def reset_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocality", []))

    @jsii.member(jsii_name="resetNotEnforceHostnames")
    def reset_not_enforce_hostnames(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotEnforceHostnames", []))

    @jsii.member(jsii_name="resetNotRequireCn")
    def reset_not_require_cn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotRequireCn", []))

    @jsii.member(jsii_name="resetOrganizationalUnits")
    def reset_organizational_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnits", []))

    @jsii.member(jsii_name="resetOrganizations")
    def reset_organizations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizations", []))

    @jsii.member(jsii_name="resetPostalCode")
    def reset_postal_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostalCode", []))

    @jsii.member(jsii_name="resetProtectCertificates")
    def reset_protect_certificates(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtectCertificates", []))

    @jsii.member(jsii_name="resetProvince")
    def reset_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvince", []))

    @jsii.member(jsii_name="resetScheduledRenew")
    def reset_scheduled_renew(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScheduledRenew", []))

    @jsii.member(jsii_name="resetServerFlag")
    def reset_server_flag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerFlag", []))

    @jsii.member(jsii_name="resetSignerKeyName")
    def reset_signer_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSignerKeyName", []))

    @jsii.member(jsii_name="resetStreetAddress")
    def reset_street_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreetAddress", []))

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
    @jsii.member(jsii_name="allowAnyNameInput")
    def allow_any_name_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowAnyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="allowCopyExtFromCsrInput")
    def allow_copy_ext_from_csr_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowCopyExtFromCsrInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedDomainsInput")
    def allowed_domains_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedExtraExtensionsInput")
    def allowed_extra_extensions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedExtraExtensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUriSansInput")
    def allowed_uri_sans_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedUriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="allowSubdomainsInput")
    def allow_subdomains_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowSubdomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="autoRenewInput")
    def auto_renew_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoRenewInput"))

    @builtins.property
    @jsii.member(jsii_name="caTargetInput")
    def ca_target_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caTargetInput"))

    @builtins.property
    @jsii.member(jsii_name="clientFlagInput")
    def client_flag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "clientFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="codeSigningFlagInput")
    def code_signing_flag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "codeSigningFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="countryInput")
    def country_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryInput"))

    @builtins.property
    @jsii.member(jsii_name="createPrivateCrlInput")
    def create_private_crl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "createPrivateCrlInput"))

    @builtins.property
    @jsii.member(jsii_name="createPublicCrlInput")
    def create_public_crl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "createPublicCrlInput"))

    @builtins.property
    @jsii.member(jsii_name="criticalKeyUsageInput")
    def critical_key_usage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "criticalKeyUsageInput"))

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
    @jsii.member(jsii_name="destinationPathInput")
    def destination_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "destinationPathInput"))

    @builtins.property
    @jsii.member(jsii_name="enableAcmeInput")
    def enable_acme_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableAcmeInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationEventInInput")
    def expiration_event_in_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "expirationEventInInput"))

    @builtins.property
    @jsii.member(jsii_name="gwClusterUrlInput")
    def gw_cluster_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gwClusterUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="isCaInput")
    def is_ca_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isCaInput"))

    @builtins.property
    @jsii.member(jsii_name="keyUsageInput")
    def key_usage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyUsageInput"))

    @builtins.property
    @jsii.member(jsii_name="localityInput")
    def locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localityInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="notEnforceHostnamesInput")
    def not_enforce_hostnames_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notEnforceHostnamesInput"))

    @builtins.property
    @jsii.member(jsii_name="notRequireCnInput")
    def not_require_cn_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "notRequireCnInput"))

    @builtins.property
    @jsii.member(jsii_name="organizationalUnitsInput")
    def organizational_units_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationalUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="organizationsInput")
    def organizations_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationsInput"))

    @builtins.property
    @jsii.member(jsii_name="postalCodeInput")
    def postal_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postalCodeInput"))

    @builtins.property
    @jsii.member(jsii_name="protectCertificatesInput")
    def protect_certificates_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "protectCertificatesInput"))

    @builtins.property
    @jsii.member(jsii_name="provinceInput")
    def province_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provinceInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduledRenewInput")
    def scheduled_renew_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scheduledRenewInput"))

    @builtins.property
    @jsii.member(jsii_name="serverFlagInput")
    def server_flag_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serverFlagInput"))

    @builtins.property
    @jsii.member(jsii_name="signerKeyNameInput")
    def signer_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signerKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="streetAddressInput")
    def street_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "streetAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="allowAnyName")
    def allow_any_name(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowAnyName"))

    @allow_any_name.setter
    def allow_any_name(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8138b3e263b915af21bf2401056c2b72283868dbaa9ba5e0fb62b4f61710f18a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowAnyName", value)

    @builtins.property
    @jsii.member(jsii_name="allowCopyExtFromCsr")
    def allow_copy_ext_from_csr(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowCopyExtFromCsr"))

    @allow_copy_ext_from_csr.setter
    def allow_copy_ext_from_csr(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc0218a9951b91a88a06bbb0b23d295f94934fba6ad190166174cb989210151a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowCopyExtFromCsr", value)

    @builtins.property
    @jsii.member(jsii_name="allowedDomains")
    def allowed_domains(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedDomains"))

    @allowed_domains.setter
    def allowed_domains(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c917b848d4ab9ad091bf168e1a8a322b8403d2c6e6fc21e88fca693cadadaf09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedDomains", value)

    @builtins.property
    @jsii.member(jsii_name="allowedExtraExtensions")
    def allowed_extra_extensions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedExtraExtensions"))

    @allowed_extra_extensions.setter
    def allowed_extra_extensions(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42a9d527b9ee7ccc2dcb716c6b3ce1b546e52d9d9728d9438dac0b4a44f381a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedExtraExtensions", value)

    @builtins.property
    @jsii.member(jsii_name="allowedUriSans")
    def allowed_uri_sans(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedUriSans"))

    @allowed_uri_sans.setter
    def allowed_uri_sans(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2331dbd1d717a9f7674323b90bedbcc06952977dfd165f460ee770da844ee74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUriSans", value)

    @builtins.property
    @jsii.member(jsii_name="allowSubdomains")
    def allow_subdomains(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowSubdomains"))

    @allow_subdomains.setter
    def allow_subdomains(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5bf39faa8c2faf17c3cab9aeea3fd6143d82cd351f9dcf441e22b9a11caf353)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowSubdomains", value)

    @builtins.property
    @jsii.member(jsii_name="autoRenew")
    def auto_renew(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoRenew"))

    @auto_renew.setter
    def auto_renew(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9924f5332d97577358b8162e0d35d6eab0cc92c1522feea209ad0fd9544cb0f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoRenew", value)

    @builtins.property
    @jsii.member(jsii_name="caTarget")
    def ca_target(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caTarget"))

    @ca_target.setter
    def ca_target(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e8764054d865e3c4e4d62c5ddfff858f6d7bf20cc2b0fafd2a350e48abd271c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caTarget", value)

    @builtins.property
    @jsii.member(jsii_name="clientFlag")
    def client_flag(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "clientFlag"))

    @client_flag.setter
    def client_flag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__020f63b5ce65eaaa1782633ef3f61e452c7bb4918a831d809af910dd75f75969)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientFlag", value)

    @builtins.property
    @jsii.member(jsii_name="codeSigningFlag")
    def code_signing_flag(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "codeSigningFlag"))

    @code_signing_flag.setter
    def code_signing_flag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad92a78d33c8659998be9443b9f4fbe845dc5308153020a171cfcdf4d2e399ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "codeSigningFlag", value)

    @builtins.property
    @jsii.member(jsii_name="country")
    def country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "country"))

    @country.setter
    def country(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6ceb6498c74a9fb35035935cbcd7d66f84dddbebfbf1b1406e80ebd789241c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "country", value)

    @builtins.property
    @jsii.member(jsii_name="createPrivateCrl")
    def create_private_crl(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "createPrivateCrl"))

    @create_private_crl.setter
    def create_private_crl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__512836209ede286a9f4c3b2b145b175cf362632bd02f74e19b37d36a2e5ae138)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createPrivateCrl", value)

    @builtins.property
    @jsii.member(jsii_name="createPublicCrl")
    def create_public_crl(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "createPublicCrl"))

    @create_public_crl.setter
    def create_public_crl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4760a7610c7f04e1b532b66f84e171ba0b7b62fac599f54aef567981dc35a97a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createPublicCrl", value)

    @builtins.property
    @jsii.member(jsii_name="criticalKeyUsage")
    def critical_key_usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "criticalKeyUsage"))

    @critical_key_usage.setter
    def critical_key_usage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ac12c5bfd692fc6569e319699a194548edb9b6b67a53400d2678c9d7b1597d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "criticalKeyUsage", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__ca020eaea2f500ab4e1e573deaaa12e133fa9b66eb10ed39ca33b1ed84861a1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8fdef02ec68db9417bae32bb89e633be0d1d13cd7e66aef3e74905c3fab788d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="destinationPath")
    def destination_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "destinationPath"))

    @destination_path.setter
    def destination_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9990cd9a964f1bb88c8deb00b6cef3a4c7f15e614ac9e2f3edb8db219d64e4c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "destinationPath", value)

    @builtins.property
    @jsii.member(jsii_name="enableAcme")
    def enable_acme(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableAcme"))

    @enable_acme.setter
    def enable_acme(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4ad17b22e5275b4ca6225f2aeea75adfe338db7a126106c1387f831ecdc9bcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableAcme", value)

    @builtins.property
    @jsii.member(jsii_name="expirationEventIn")
    def expiration_event_in(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "expirationEventIn"))

    @expiration_event_in.setter
    def expiration_event_in(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e94e59726333833cff30ed0e9c1d4d960612a7a24a70e6ab5fff52bfa094861)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationEventIn", value)

    @builtins.property
    @jsii.member(jsii_name="gwClusterUrl")
    def gw_cluster_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gwClusterUrl"))

    @gw_cluster_url.setter
    def gw_cluster_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93632af77e234d0dbce9e2ddea42d2a223275a2a514269217e3522d5d51702ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gwClusterUrl", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c769cdbd243ce353190d4e7e66e98e2a08d52485f826f3372426a8694ec3e2a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="isCa")
    def is_ca(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isCa"))

    @is_ca.setter
    def is_ca(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5061992bfac950b31a52d108362bad39a1c554ec0312e33c0e4636ff1fa23a35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isCa", value)

    @builtins.property
    @jsii.member(jsii_name="keyUsage")
    def key_usage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyUsage"))

    @key_usage.setter
    def key_usage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__619a1e5612845f1df5dfbb79ff81d645e64c388c84da6a600e19c2e6007b2fd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyUsage", value)

    @builtins.property
    @jsii.member(jsii_name="locality")
    def locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locality"))

    @locality.setter
    def locality(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f12f597e47bbcb13752a85010bddea61b86d99baba93c0177b7c8011911d51e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "locality", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd5bccd6882268900aa64e5dafed5c9d5c12b80de50bf861d97daf174e43ebb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="notEnforceHostnames")
    def not_enforce_hostnames(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "notEnforceHostnames"))

    @not_enforce_hostnames.setter
    def not_enforce_hostnames(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a7b12d6042282d4ba0b827bb2c28cc9c38c90ac798dc131e28370d8fe70b0c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notEnforceHostnames", value)

    @builtins.property
    @jsii.member(jsii_name="notRequireCn")
    def not_require_cn(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "notRequireCn"))

    @not_require_cn.setter
    def not_require_cn(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7696172ea4ffd29cc57fdbe8f6b47b13dbbd23de5fd9ee90dad97ac5dd94055)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notRequireCn", value)

    @builtins.property
    @jsii.member(jsii_name="organizationalUnits")
    def organizational_units(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnits"))

    @organizational_units.setter
    def organizational_units(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__637d2f510ede129eb2cabc32b709be545fb11c7de83fef020032243a17b6707d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizationalUnits", value)

    @builtins.property
    @jsii.member(jsii_name="organizations")
    def organizations(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizations"))

    @organizations.setter
    def organizations(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b296d5e1785a39a846255394669b795f56a3649a286d5b7de99473bed1f15f33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organizations", value)

    @builtins.property
    @jsii.member(jsii_name="postalCode")
    def postal_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postalCode"))

    @postal_code.setter
    def postal_code(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5a255060b59b78898e5b7a3afbfd448aca12cbd8e63f4273d54e1494d78f617)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postalCode", value)

    @builtins.property
    @jsii.member(jsii_name="protectCertificates")
    def protect_certificates(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "protectCertificates"))

    @protect_certificates.setter
    def protect_certificates(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a88ac9acea41ff4aa12fc843986a19a54eec3ab724e769de26c34d6f887924f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protectCertificates", value)

    @builtins.property
    @jsii.member(jsii_name="province")
    def province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "province"))

    @province.setter
    def province(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__315acf8dd6222988393d2b1e8bc13026b77679106104eda09e06185a9ad1c0a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "province", value)

    @builtins.property
    @jsii.member(jsii_name="scheduledRenew")
    def scheduled_renew(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scheduledRenew"))

    @scheduled_renew.setter
    def scheduled_renew(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e6e4c00575e4d9b9b733eb385c6d0ee60a4907318945f54192fcc44f44aac81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scheduledRenew", value)

    @builtins.property
    @jsii.member(jsii_name="serverFlag")
    def server_flag(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serverFlag"))

    @server_flag.setter
    def server_flag(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__794f6583afd7873b62d7b1bf0c9ac157d1170b528a4713240ee4c26a0eba8f5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverFlag", value)

    @builtins.property
    @jsii.member(jsii_name="signerKeyName")
    def signer_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signerKeyName"))

    @signer_key_name.setter
    def signer_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33259873f3afa5a89c2a257d4afc0ccd4b8e9fcf56e10a58bd8030d4299c5603)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signerKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="streetAddress")
    def street_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "streetAddress"))

    @street_address.setter
    def street_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e7f5411640013fccb7c7e4a1a4c6fb659b5dc7b120f4cd798a4d3c126ca01ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "streetAddress", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe9f61ec5cf906f34b44a008dbddf23121de328fb19555a15bb5c99b77dc47f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea5ead83ebbd87188199a80570a19272d3f9184e8999d63e1b45a6ae97941073)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value)


@jsii.data_type(
    jsii_type="akeyless.pkiCertIssuer.PkiCertIssuerConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "ttl": "ttl",
        "allow_any_name": "allowAnyName",
        "allow_copy_ext_from_csr": "allowCopyExtFromCsr",
        "allowed_domains": "allowedDomains",
        "allowed_extra_extensions": "allowedExtraExtensions",
        "allowed_uri_sans": "allowedUriSans",
        "allow_subdomains": "allowSubdomains",
        "auto_renew": "autoRenew",
        "ca_target": "caTarget",
        "client_flag": "clientFlag",
        "code_signing_flag": "codeSigningFlag",
        "country": "country",
        "create_private_crl": "createPrivateCrl",
        "create_public_crl": "createPublicCrl",
        "critical_key_usage": "criticalKeyUsage",
        "delete_protection": "deleteProtection",
        "description": "description",
        "destination_path": "destinationPath",
        "enable_acme": "enableAcme",
        "expiration_event_in": "expirationEventIn",
        "gw_cluster_url": "gwClusterUrl",
        "id": "id",
        "is_ca": "isCa",
        "key_usage": "keyUsage",
        "locality": "locality",
        "not_enforce_hostnames": "notEnforceHostnames",
        "not_require_cn": "notRequireCn",
        "organizational_units": "organizationalUnits",
        "organizations": "organizations",
        "postal_code": "postalCode",
        "protect_certificates": "protectCertificates",
        "province": "province",
        "scheduled_renew": "scheduledRenew",
        "server_flag": "serverFlag",
        "signer_key_name": "signerKeyName",
        "street_address": "streetAddress",
        "tags": "tags",
    },
)
class PkiCertIssuerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        ttl: builtins.str,
        allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allow_copy_ext_from_csr: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        allowed_domains: typing.Optional[builtins.str] = None,
        allowed_extra_extensions: typing.Optional[builtins.str] = None,
        allowed_uri_sans: typing.Optional[builtins.str] = None,
        allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ca_target: typing.Optional[builtins.str] = None,
        client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        country: typing.Optional[builtins.str] = None,
        create_private_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        create_public_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        critical_key_usage: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        destination_path: typing.Optional[builtins.str] = None,
        enable_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        gw_cluster_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        is_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        key_usage: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        not_enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        not_require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        organizational_units: typing.Optional[builtins.str] = None,
        organizations: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        protect_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        province: typing.Optional[builtins.str] = None,
        scheduled_renew: typing.Optional[jsii.Number] = None,
        server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        signer_key_name: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[builtins.str] = None,
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
        :param name: PKI certificate issuer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#name PkiCertIssuer#name}
        :param ttl: The maximum requested Time To Live for issued certificate by default in seconds, supported formats are s,m,h,d. In case of Public CA, this is based on the CA target's supported maximum TTLs Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#ttl PkiCertIssuer#ttl}
        :param allow_any_name: If set, clients can request certificates for any CN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_any_name PkiCertIssuer#allow_any_name}
        :param allow_copy_ext_from_csr: If set, will allow copying the extra extensions from the csr file (if given). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_copy_ext_from_csr PkiCertIssuer#allow_copy_ext_from_csr}
        :param allowed_domains: A list of the allowed domains that clients can request to be included in the certificate (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_domains PkiCertIssuer#allowed_domains}
        :param allowed_extra_extensions: A json string that defines the allowed extra extensions for the pki cert issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_extra_extensions PkiCertIssuer#allowed_extra_extensions}
        :param allowed_uri_sans: A list of the allowed URIs that clients can request to be included in the certificate as part of the URI Subject Alternative Names (in a comma-delimited list). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_uri_sans PkiCertIssuer#allowed_uri_sans}
        :param allow_subdomains: If set, clients can request certificates for subdomains and wildcard subdomains of the allowed domains. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_subdomains PkiCertIssuer#allow_subdomains}
        :param auto_renew: Automatically renew certificates before expiration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#auto_renew PkiCertIssuer#auto_renew}
        :param ca_target: The name of an existing CA target to attach this PKI Certificate Issuer to, required in Public CA mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#ca_target PkiCertIssuer#ca_target}
        :param client_flag: If set, certificates will be flagged for client auth use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#client_flag PkiCertIssuer#client_flag}
        :param code_signing_flag: If set, certificates will be flagged for code signing use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#code_signing_flag PkiCertIssuer#code_signing_flag}
        :param country: A comma-separated list of countries that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#country PkiCertIssuer#country}
        :param create_private_crl: Set this to allow the issuer will expose a CRL endpoint in the Gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#create_private_crl PkiCertIssuer#create_private_crl}
        :param create_public_crl: Set this to allow the cert issuer will expose a public CRL endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#create_public_crl PkiCertIssuer#create_public_crl}
        :param critical_key_usage: Mark key usage as critical [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#critical_key_usage PkiCertIssuer#critical_key_usage}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#delete_protection PkiCertIssuer#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#description PkiCertIssuer#description}
        :param destination_path: A path in Akeyless which to save generated certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#destination_path PkiCertIssuer#destination_path}
        :param enable_acme: If set, the cert issuer will support the acme protocol. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#enable_acme PkiCertIssuer#enable_acme}
        :param expiration_event_in: How many days before the expiration of the certificate would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#expiration_event_in PkiCertIssuer#expiration_event_in}
        :param gw_cluster_url: The GW cluster URL to issue the certificate from, required in Public CA mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#gw_cluster_url PkiCertIssuer#gw_cluster_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#id PkiCertIssuer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_ca: If set, the basic constraints extension will be added to certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#is_ca PkiCertIssuer#is_ca}
        :param key_usage: A comma-separated string or list of key usages. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#key_usage PkiCertIssuer#key_usage}
        :param locality: A comma-separated list of localities that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#locality PkiCertIssuer#locality}
        :param not_enforce_hostnames: If set, any names are allowed for CN and SANs in the certificate and not only a valid host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#not_enforce_hostnames PkiCertIssuer#not_enforce_hostnames}
        :param not_require_cn: If set, clients can request certificates without a CN. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#not_require_cn PkiCertIssuer#not_require_cn}
        :param organizational_units: A comma-separated list of organizational units (OU) that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#organizational_units PkiCertIssuer#organizational_units}
        :param organizations: A comma-separated list of organizations (O) that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#organizations PkiCertIssuer#organizations}
        :param postal_code: A comma-separated list of postal codes that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#postal_code PkiCertIssuer#postal_code}
        :param protect_certificates: Whether to protect generated certificates from deletion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#protect_certificates PkiCertIssuer#protect_certificates}
        :param province: A comma-separated list of provinces that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#province PkiCertIssuer#province}
        :param scheduled_renew: Number of days before expiration to renew certificates. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#scheduled_renew PkiCertIssuer#scheduled_renew}
        :param server_flag: If set, certificates will be flagged for server auth use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#server_flag PkiCertIssuer#server_flag}
        :param signer_key_name: A key to sign the certificate with, required in Private CA mode. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#signer_key_name PkiCertIssuer#signer_key_name}
        :param street_address: A comma-separated list of street addresses that will be set in the issued certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#street_address PkiCertIssuer#street_address}
        :param tags: List of the tags attached to this key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#tags PkiCertIssuer#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae3c95b985546fd5a84ad11b653a47f3672476625e48492e7d63c8c8abc71d5b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument allow_any_name", value=allow_any_name, expected_type=type_hints["allow_any_name"])
            check_type(argname="argument allow_copy_ext_from_csr", value=allow_copy_ext_from_csr, expected_type=type_hints["allow_copy_ext_from_csr"])
            check_type(argname="argument allowed_domains", value=allowed_domains, expected_type=type_hints["allowed_domains"])
            check_type(argname="argument allowed_extra_extensions", value=allowed_extra_extensions, expected_type=type_hints["allowed_extra_extensions"])
            check_type(argname="argument allowed_uri_sans", value=allowed_uri_sans, expected_type=type_hints["allowed_uri_sans"])
            check_type(argname="argument allow_subdomains", value=allow_subdomains, expected_type=type_hints["allow_subdomains"])
            check_type(argname="argument auto_renew", value=auto_renew, expected_type=type_hints["auto_renew"])
            check_type(argname="argument ca_target", value=ca_target, expected_type=type_hints["ca_target"])
            check_type(argname="argument client_flag", value=client_flag, expected_type=type_hints["client_flag"])
            check_type(argname="argument code_signing_flag", value=code_signing_flag, expected_type=type_hints["code_signing_flag"])
            check_type(argname="argument country", value=country, expected_type=type_hints["country"])
            check_type(argname="argument create_private_crl", value=create_private_crl, expected_type=type_hints["create_private_crl"])
            check_type(argname="argument create_public_crl", value=create_public_crl, expected_type=type_hints["create_public_crl"])
            check_type(argname="argument critical_key_usage", value=critical_key_usage, expected_type=type_hints["critical_key_usage"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument destination_path", value=destination_path, expected_type=type_hints["destination_path"])
            check_type(argname="argument enable_acme", value=enable_acme, expected_type=type_hints["enable_acme"])
            check_type(argname="argument expiration_event_in", value=expiration_event_in, expected_type=type_hints["expiration_event_in"])
            check_type(argname="argument gw_cluster_url", value=gw_cluster_url, expected_type=type_hints["gw_cluster_url"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument is_ca", value=is_ca, expected_type=type_hints["is_ca"])
            check_type(argname="argument key_usage", value=key_usage, expected_type=type_hints["key_usage"])
            check_type(argname="argument locality", value=locality, expected_type=type_hints["locality"])
            check_type(argname="argument not_enforce_hostnames", value=not_enforce_hostnames, expected_type=type_hints["not_enforce_hostnames"])
            check_type(argname="argument not_require_cn", value=not_require_cn, expected_type=type_hints["not_require_cn"])
            check_type(argname="argument organizational_units", value=organizational_units, expected_type=type_hints["organizational_units"])
            check_type(argname="argument organizations", value=organizations, expected_type=type_hints["organizations"])
            check_type(argname="argument postal_code", value=postal_code, expected_type=type_hints["postal_code"])
            check_type(argname="argument protect_certificates", value=protect_certificates, expected_type=type_hints["protect_certificates"])
            check_type(argname="argument province", value=province, expected_type=type_hints["province"])
            check_type(argname="argument scheduled_renew", value=scheduled_renew, expected_type=type_hints["scheduled_renew"])
            check_type(argname="argument server_flag", value=server_flag, expected_type=type_hints["server_flag"])
            check_type(argname="argument signer_key_name", value=signer_key_name, expected_type=type_hints["signer_key_name"])
            check_type(argname="argument street_address", value=street_address, expected_type=type_hints["street_address"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "ttl": ttl,
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
        if allow_any_name is not None:
            self._values["allow_any_name"] = allow_any_name
        if allow_copy_ext_from_csr is not None:
            self._values["allow_copy_ext_from_csr"] = allow_copy_ext_from_csr
        if allowed_domains is not None:
            self._values["allowed_domains"] = allowed_domains
        if allowed_extra_extensions is not None:
            self._values["allowed_extra_extensions"] = allowed_extra_extensions
        if allowed_uri_sans is not None:
            self._values["allowed_uri_sans"] = allowed_uri_sans
        if allow_subdomains is not None:
            self._values["allow_subdomains"] = allow_subdomains
        if auto_renew is not None:
            self._values["auto_renew"] = auto_renew
        if ca_target is not None:
            self._values["ca_target"] = ca_target
        if client_flag is not None:
            self._values["client_flag"] = client_flag
        if code_signing_flag is not None:
            self._values["code_signing_flag"] = code_signing_flag
        if country is not None:
            self._values["country"] = country
        if create_private_crl is not None:
            self._values["create_private_crl"] = create_private_crl
        if create_public_crl is not None:
            self._values["create_public_crl"] = create_public_crl
        if critical_key_usage is not None:
            self._values["critical_key_usage"] = critical_key_usage
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if destination_path is not None:
            self._values["destination_path"] = destination_path
        if enable_acme is not None:
            self._values["enable_acme"] = enable_acme
        if expiration_event_in is not None:
            self._values["expiration_event_in"] = expiration_event_in
        if gw_cluster_url is not None:
            self._values["gw_cluster_url"] = gw_cluster_url
        if id is not None:
            self._values["id"] = id
        if is_ca is not None:
            self._values["is_ca"] = is_ca
        if key_usage is not None:
            self._values["key_usage"] = key_usage
        if locality is not None:
            self._values["locality"] = locality
        if not_enforce_hostnames is not None:
            self._values["not_enforce_hostnames"] = not_enforce_hostnames
        if not_require_cn is not None:
            self._values["not_require_cn"] = not_require_cn
        if organizational_units is not None:
            self._values["organizational_units"] = organizational_units
        if organizations is not None:
            self._values["organizations"] = organizations
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if protect_certificates is not None:
            self._values["protect_certificates"] = protect_certificates
        if province is not None:
            self._values["province"] = province
        if scheduled_renew is not None:
            self._values["scheduled_renew"] = scheduled_renew
        if server_flag is not None:
            self._values["server_flag"] = server_flag
        if signer_key_name is not None:
            self._values["signer_key_name"] = signer_key_name
        if street_address is not None:
            self._values["street_address"] = street_address
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
    def name(self) -> builtins.str:
        '''PKI certificate issuer name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#name PkiCertIssuer#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> builtins.str:
        '''The maximum requested Time To Live for issued certificate by default in seconds, supported formats are s,m,h,d.

        In case of Public CA, this is based on the CA target's supported maximum TTLs

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#ttl PkiCertIssuer#ttl}
        '''
        result = self._values.get("ttl")
        assert result is not None, "Required property 'ttl' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allow_any_name(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, clients can request certificates for any CN.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_any_name PkiCertIssuer#allow_any_name}
        '''
        result = self._values.get("allow_any_name")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allow_copy_ext_from_csr(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, will allow copying the extra extensions from the csr file (if given).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_copy_ext_from_csr PkiCertIssuer#allow_copy_ext_from_csr}
        '''
        result = self._values.get("allow_copy_ext_from_csr")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def allowed_domains(self) -> typing.Optional[builtins.str]:
        '''A list of the allowed domains that clients can request to be included in the certificate (in a comma-delimited list).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_domains PkiCertIssuer#allowed_domains}
        '''
        result = self._values.get("allowed_domains")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_extra_extensions(self) -> typing.Optional[builtins.str]:
        '''A json string that defines the allowed extra extensions for the pki cert issuer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_extra_extensions PkiCertIssuer#allowed_extra_extensions}
        '''
        result = self._values.get("allowed_extra_extensions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allowed_uri_sans(self) -> typing.Optional[builtins.str]:
        '''A list of the allowed URIs that clients can request to be included in the certificate as part of the URI Subject Alternative Names (in a comma-delimited list).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allowed_uri_sans PkiCertIssuer#allowed_uri_sans}
        '''
        result = self._values.get("allowed_uri_sans")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def allow_subdomains(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, clients can request certificates for subdomains and wildcard subdomains of the allowed domains.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#allow_subdomains PkiCertIssuer#allow_subdomains}
        '''
        result = self._values.get("allow_subdomains")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_renew(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Automatically renew certificates before expiration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#auto_renew PkiCertIssuer#auto_renew}
        '''
        result = self._values.get("auto_renew")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ca_target(self) -> typing.Optional[builtins.str]:
        '''The name of an existing CA target to attach this PKI Certificate Issuer to, required in Public CA mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#ca_target PkiCertIssuer#ca_target}
        '''
        result = self._values.get("ca_target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_flag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, certificates will be flagged for client auth use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#client_flag PkiCertIssuer#client_flag}
        '''
        result = self._values.get("client_flag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def code_signing_flag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, certificates will be flagged for code signing use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#code_signing_flag PkiCertIssuer#code_signing_flag}
        '''
        result = self._values.get("code_signing_flag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of countries that will be set in the issued certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#country PkiCertIssuer#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def create_private_crl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set this to allow the issuer will expose a CRL endpoint in the Gateway.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#create_private_crl PkiCertIssuer#create_private_crl}
        '''
        result = self._values.get("create_private_crl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def create_public_crl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set this to allow the cert issuer will expose a public CRL endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#create_public_crl PkiCertIssuer#create_public_crl}
        '''
        result = self._values.get("create_public_crl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def critical_key_usage(self) -> typing.Optional[builtins.str]:
        '''Mark key usage as critical [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#critical_key_usage PkiCertIssuer#critical_key_usage}
        '''
        result = self._values.get("critical_key_usage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Protection from accidental deletion of this item, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#delete_protection PkiCertIssuer#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#description PkiCertIssuer#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def destination_path(self) -> typing.Optional[builtins.str]:
        '''A path in Akeyless which to save generated certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#destination_path PkiCertIssuer#destination_path}
        '''
        result = self._values.get("destination_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_acme(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, the cert issuer will support the acme protocol.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#enable_acme PkiCertIssuer#enable_acme}
        '''
        result = self._values.get("enable_acme")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def expiration_event_in(self) -> typing.Optional[typing.List[builtins.str]]:
        '''How many days before the expiration of the certificate would you like to be notified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#expiration_event_in PkiCertIssuer#expiration_event_in}
        '''
        result = self._values.get("expiration_event_in")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def gw_cluster_url(self) -> typing.Optional[builtins.str]:
        '''The GW cluster URL to issue the certificate from, required in Public CA mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#gw_cluster_url PkiCertIssuer#gw_cluster_url}
        '''
        result = self._values.get("gw_cluster_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#id PkiCertIssuer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_ca(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, the basic constraints extension will be added to certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#is_ca PkiCertIssuer#is_ca}
        '''
        result = self._values.get("is_ca")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def key_usage(self) -> typing.Optional[builtins.str]:
        '''A comma-separated string or list of key usages.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#key_usage PkiCertIssuer#key_usage}
        '''
        result = self._values.get("key_usage")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of localities that will be set in the issued certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#locality PkiCertIssuer#locality}
        '''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def not_enforce_hostnames(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, any names are allowed for CN and SANs in the certificate and not only a valid host name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#not_enforce_hostnames PkiCertIssuer#not_enforce_hostnames}
        '''
        result = self._values.get("not_enforce_hostnames")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def not_require_cn(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, clients can request certificates without a CN.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#not_require_cn PkiCertIssuer#not_require_cn}
        '''
        result = self._values.get("not_require_cn")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def organizational_units(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of organizational units (OU) that will be set in the issued certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#organizational_units PkiCertIssuer#organizational_units}
        '''
        result = self._values.get("organizational_units")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizations(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of organizations (O) that will be set in the issued certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#organizations PkiCertIssuer#organizations}
        '''
        result = self._values.get("organizations")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of postal codes that will be set in the issued certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#postal_code PkiCertIssuer#postal_code}
        '''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protect_certificates(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to protect generated certificates from deletion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#protect_certificates PkiCertIssuer#protect_certificates}
        '''
        result = self._values.get("protect_certificates")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of provinces that will be set in the issued certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#province PkiCertIssuer#province}
        '''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scheduled_renew(self) -> typing.Optional[jsii.Number]:
        '''Number of days before expiration to renew certificates.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#scheduled_renew PkiCertIssuer#scheduled_renew}
        '''
        result = self._values.get("scheduled_renew")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_flag(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''If set, certificates will be flagged for server auth use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#server_flag PkiCertIssuer#server_flag}
        '''
        result = self._values.get("server_flag")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def signer_key_name(self) -> typing.Optional[builtins.str]:
        '''A key to sign the certificate with, required in Private CA mode.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#signer_key_name PkiCertIssuer#signer_key_name}
        '''
        result = self._values.get("signer_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def street_address(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list of street addresses that will be set in the issued certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#street_address PkiCertIssuer#street_address}
        '''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/pki_cert_issuer#tags PkiCertIssuer#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PkiCertIssuerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "PkiCertIssuer",
    "PkiCertIssuerConfig",
]

publication.publish()

def _typecheckingstub__55917388f2ead456038a2b7821b39910718c10abf2a4f5d997e574d418fa26a7(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    ttl: builtins.str,
    allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_copy_ext_from_csr: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_domains: typing.Optional[builtins.str] = None,
    allowed_extra_extensions: typing.Optional[builtins.str] = None,
    allowed_uri_sans: typing.Optional[builtins.str] = None,
    allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ca_target: typing.Optional[builtins.str] = None,
    client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    country: typing.Optional[builtins.str] = None,
    create_private_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    create_public_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    critical_key_usage: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    destination_path: typing.Optional[builtins.str] = None,
    enable_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    gw_cluster_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    is_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    key_usage: typing.Optional[builtins.str] = None,
    locality: typing.Optional[builtins.str] = None,
    not_enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    not_require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    organizational_units: typing.Optional[builtins.str] = None,
    organizations: typing.Optional[builtins.str] = None,
    postal_code: typing.Optional[builtins.str] = None,
    protect_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    province: typing.Optional[builtins.str] = None,
    scheduled_renew: typing.Optional[jsii.Number] = None,
    server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    signer_key_name: typing.Optional[builtins.str] = None,
    street_address: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__434f722227df60f716d054150de2c9384cfcfff7d8141f0b9fd19321f3f3e6ec(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8138b3e263b915af21bf2401056c2b72283868dbaa9ba5e0fb62b4f61710f18a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc0218a9951b91a88a06bbb0b23d295f94934fba6ad190166174cb989210151a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c917b848d4ab9ad091bf168e1a8a322b8403d2c6e6fc21e88fca693cadadaf09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42a9d527b9ee7ccc2dcb716c6b3ce1b546e52d9d9728d9438dac0b4a44f381a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2331dbd1d717a9f7674323b90bedbcc06952977dfd165f460ee770da844ee74(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5bf39faa8c2faf17c3cab9aeea3fd6143d82cd351f9dcf441e22b9a11caf353(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9924f5332d97577358b8162e0d35d6eab0cc92c1522feea209ad0fd9544cb0f8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e8764054d865e3c4e4d62c5ddfff858f6d7bf20cc2b0fafd2a350e48abd271c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__020f63b5ce65eaaa1782633ef3f61e452c7bb4918a831d809af910dd75f75969(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad92a78d33c8659998be9443b9f4fbe845dc5308153020a171cfcdf4d2e399ef(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6ceb6498c74a9fb35035935cbcd7d66f84dddbebfbf1b1406e80ebd789241c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__512836209ede286a9f4c3b2b145b175cf362632bd02f74e19b37d36a2e5ae138(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4760a7610c7f04e1b532b66f84e171ba0b7b62fac599f54aef567981dc35a97a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ac12c5bfd692fc6569e319699a194548edb9b6b67a53400d2678c9d7b1597d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca020eaea2f500ab4e1e573deaaa12e133fa9b66eb10ed39ca33b1ed84861a1e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8fdef02ec68db9417bae32bb89e633be0d1d13cd7e66aef3e74905c3fab788d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9990cd9a964f1bb88c8deb00b6cef3a4c7f15e614ac9e2f3edb8db219d64e4c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4ad17b22e5275b4ca6225f2aeea75adfe338db7a126106c1387f831ecdc9bcd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e94e59726333833cff30ed0e9c1d4d960612a7a24a70e6ab5fff52bfa094861(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93632af77e234d0dbce9e2ddea42d2a223275a2a514269217e3522d5d51702ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c769cdbd243ce353190d4e7e66e98e2a08d52485f826f3372426a8694ec3e2a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5061992bfac950b31a52d108362bad39a1c554ec0312e33c0e4636ff1fa23a35(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__619a1e5612845f1df5dfbb79ff81d645e64c388c84da6a600e19c2e6007b2fd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f12f597e47bbcb13752a85010bddea61b86d99baba93c0177b7c8011911d51e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd5bccd6882268900aa64e5dafed5c9d5c12b80de50bf861d97daf174e43ebb7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a7b12d6042282d4ba0b827bb2c28cc9c38c90ac798dc131e28370d8fe70b0c8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7696172ea4ffd29cc57fdbe8f6b47b13dbbd23de5fd9ee90dad97ac5dd94055(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__637d2f510ede129eb2cabc32b709be545fb11c7de83fef020032243a17b6707d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b296d5e1785a39a846255394669b795f56a3649a286d5b7de99473bed1f15f33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5a255060b59b78898e5b7a3afbfd448aca12cbd8e63f4273d54e1494d78f617(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88ac9acea41ff4aa12fc843986a19a54eec3ab724e769de26c34d6f887924f9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__315acf8dd6222988393d2b1e8bc13026b77679106104eda09e06185a9ad1c0a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e6e4c00575e4d9b9b733eb385c6d0ee60a4907318945f54192fcc44f44aac81(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__794f6583afd7873b62d7b1bf0c9ac157d1170b528a4713240ee4c26a0eba8f5a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33259873f3afa5a89c2a257d4afc0ccd4b8e9fcf56e10a58bd8030d4299c5603(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e7f5411640013fccb7c7e4a1a4c6fb659b5dc7b120f4cd798a4d3c126ca01ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe9f61ec5cf906f34b44a008dbddf23121de328fb19555a15bb5c99b77dc47f0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea5ead83ebbd87188199a80570a19272d3f9184e8999d63e1b45a6ae97941073(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae3c95b985546fd5a84ad11b653a47f3672476625e48492e7d63c8c8abc71d5b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    ttl: builtins.str,
    allow_any_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allow_copy_ext_from_csr: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    allowed_domains: typing.Optional[builtins.str] = None,
    allowed_extra_extensions: typing.Optional[builtins.str] = None,
    allowed_uri_sans: typing.Optional[builtins.str] = None,
    allow_subdomains: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_renew: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ca_target: typing.Optional[builtins.str] = None,
    client_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    code_signing_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    country: typing.Optional[builtins.str] = None,
    create_private_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    create_public_crl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    critical_key_usage: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    destination_path: typing.Optional[builtins.str] = None,
    enable_acme: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    gw_cluster_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    is_ca: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    key_usage: typing.Optional[builtins.str] = None,
    locality: typing.Optional[builtins.str] = None,
    not_enforce_hostnames: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    not_require_cn: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    organizational_units: typing.Optional[builtins.str] = None,
    organizations: typing.Optional[builtins.str] = None,
    postal_code: typing.Optional[builtins.str] = None,
    protect_certificates: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    province: typing.Optional[builtins.str] = None,
    scheduled_renew: typing.Optional[jsii.Number] = None,
    server_flag: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    signer_key_name: typing.Optional[builtins.str] = None,
    street_address: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
