'''
# `akeyless_auth_method_cert`

Refer to the Terraform Registry for docs: [`akeyless_auth_method_cert`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert).
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


class AuthMethodCert(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethodCert.AuthMethodCert",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert akeyless_auth_method_cert}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        unique_identifier: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        certificate_data: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        revoked_cert_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert akeyless_auth_method_cert} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#name AuthMethodCert#name}
        :param unique_identifier: A unique identifier (ID) value should be configured for OIDC, OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#unique_identifier AuthMethodCert#unique_identifier}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#access_expires AuthMethodCert#access_expires}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#audit_logs_claims AuthMethodCert#audit_logs_claims}
        :param bound_common_names: A list of names. At least one must exist in the Common Name. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_common_names AuthMethodCert#bound_common_names}
        :param bound_dns_sans: A list of DNS names. At least one must exist in the SANs. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_dns_sans AuthMethodCert#bound_dns_sans}
        :param bound_email_sans: A list of Email Addresses. At least one must exist in the SANs. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_email_sans AuthMethodCert#bound_email_sans}
        :param bound_extensions: A list of extensions formatted as 'oid:value'. Expects the extension value to be some type of ASN1 encoded string. All values much match. Supports globbing on 'value'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_extensions AuthMethodCert#bound_extensions}
        :param bound_ips: A comma-separated CIDR block list to allow client access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_ips AuthMethodCert#bound_ips}
        :param bound_organizational_units: A list of Organizational Units names. At least one must exist in the OU field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_organizational_units AuthMethodCert#bound_organizational_units}
        :param bound_uri_sans: A list of URIs. At least one must exist in the SANs. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_uri_sans AuthMethodCert#bound_uri_sans}
        :param certificate_data: The certificate data in base64, if no file was provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#certificate_data AuthMethodCert#certificate_data}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#delete_protection AuthMethodCert#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#force_sub_claims AuthMethodCert#force_sub_claims}
        :param gw_bound_ips: A comma-separated CIDR block list as a trusted Gateway entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#gw_bound_ips AuthMethodCert#gw_bound_ips}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#id AuthMethodCert#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#jwt_ttl AuthMethodCert#jwt_ttl}
        :param revoked_cert_ids: A list of revoked cert ids. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#revoked_cert_ids AuthMethodCert#revoked_cert_ids}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecdad21be499102013f77137326f33474e178c860ef70d2a0bf5c60af900e2bf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodCertConfig(
            name=name,
            unique_identifier=unique_identifier,
            access_expires=access_expires,
            audit_logs_claims=audit_logs_claims,
            bound_common_names=bound_common_names,
            bound_dns_sans=bound_dns_sans,
            bound_email_sans=bound_email_sans,
            bound_extensions=bound_extensions,
            bound_ips=bound_ips,
            bound_organizational_units=bound_organizational_units,
            bound_uri_sans=bound_uri_sans,
            certificate_data=certificate_data,
            delete_protection=delete_protection,
            force_sub_claims=force_sub_claims,
            gw_bound_ips=gw_bound_ips,
            id=id,
            jwt_ttl=jwt_ttl,
            revoked_cert_ids=revoked_cert_ids,
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
        '''Generates CDKTF code for importing a AuthMethodCert resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethodCert to import.
        :param import_from_id: The id of the existing AuthMethodCert that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethodCert to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d41424b06e6326add650ecabc4aad5e892ad1e60510a6475bcf3330236a0e772)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessExpires")
    def reset_access_expires(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessExpires", []))

    @jsii.member(jsii_name="resetAuditLogsClaims")
    def reset_audit_logs_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditLogsClaims", []))

    @jsii.member(jsii_name="resetBoundCommonNames")
    def reset_bound_common_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundCommonNames", []))

    @jsii.member(jsii_name="resetBoundDnsSans")
    def reset_bound_dns_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundDnsSans", []))

    @jsii.member(jsii_name="resetBoundEmailSans")
    def reset_bound_email_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundEmailSans", []))

    @jsii.member(jsii_name="resetBoundExtensions")
    def reset_bound_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundExtensions", []))

    @jsii.member(jsii_name="resetBoundIps")
    def reset_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIps", []))

    @jsii.member(jsii_name="resetBoundOrganizationalUnits")
    def reset_bound_organizational_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundOrganizationalUnits", []))

    @jsii.member(jsii_name="resetBoundUriSans")
    def reset_bound_uri_sans(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundUriSans", []))

    @jsii.member(jsii_name="resetCertificateData")
    def reset_certificate_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateData", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetForceSubClaims")
    def reset_force_sub_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceSubClaims", []))

    @jsii.member(jsii_name="resetGwBoundIps")
    def reset_gw_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGwBoundIps", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJwtTtl")
    def reset_jwt_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtTtl", []))

    @jsii.member(jsii_name="resetRevokedCertIds")
    def reset_revoked_cert_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevokedCertIds", []))

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
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @builtins.property
    @jsii.member(jsii_name="accessExpiresInput")
    def access_expires_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessExpiresInput"))

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaimsInput")
    def audit_logs_claims_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "auditLogsClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundCommonNamesInput")
    def bound_common_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundCommonNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundDnsSansInput")
    def bound_dns_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundDnsSansInput"))

    @builtins.property
    @jsii.member(jsii_name="boundEmailSansInput")
    def bound_email_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundEmailSansInput"))

    @builtins.property
    @jsii.member(jsii_name="boundExtensionsInput")
    def bound_extensions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundExtensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIpsInput")
    def bound_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundOrganizationalUnitsInput")
    def bound_organizational_units_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundOrganizationalUnitsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundUriSansInput")
    def bound_uri_sans_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundUriSansInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateDataInput")
    def certificate_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateDataInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="forceSubClaimsInput")
    def force_sub_claims_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceSubClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="gwBoundIpsInput")
    def gw_bound_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "gwBoundIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtTtlInput")
    def jwt_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "jwtTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="revokedCertIdsInput")
    def revoked_cert_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "revokedCertIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="uniqueIdentifierInput")
    def unique_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uniqueIdentifierInput"))

    @builtins.property
    @jsii.member(jsii_name="accessExpires")
    def access_expires(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessExpires"))

    @access_expires.setter
    def access_expires(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2dcdaf13df142f9e3ad48eeb3a33aa6b5122d15cd002b641f74f0753d5ceae57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaims")
    def audit_logs_claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditLogsClaims"))

    @audit_logs_claims.setter
    def audit_logs_claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7a026bdd8ee53b77b010a50746aaa0b8405e6f39f46088429455a4d165cd3b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditLogsClaims", value)

    @builtins.property
    @jsii.member(jsii_name="boundCommonNames")
    def bound_common_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundCommonNames"))

    @bound_common_names.setter
    def bound_common_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f24de86ced3e57fd7d30bb30663a7638b983f8ee79d55a32224960e79da80301)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundCommonNames", value)

    @builtins.property
    @jsii.member(jsii_name="boundDnsSans")
    def bound_dns_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundDnsSans"))

    @bound_dns_sans.setter
    def bound_dns_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4e5f26f73b29bf054754264aecf8214c4fb4a4c7733c3b8b7778b9c9083c460)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundDnsSans", value)

    @builtins.property
    @jsii.member(jsii_name="boundEmailSans")
    def bound_email_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundEmailSans"))

    @bound_email_sans.setter
    def bound_email_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9aca1e9e12db2b23effbda69b76afba512a5387000b89d7da9e8ea6152741b58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundEmailSans", value)

    @builtins.property
    @jsii.member(jsii_name="boundExtensions")
    def bound_extensions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundExtensions"))

    @bound_extensions.setter
    def bound_extensions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25417c6b23fe5927e98631576c7df0ff39355f83ff02882e7bb747b109b6037e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundExtensions", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__124d03521013f883ffb944311efc451f2eab4ce6fd24c7126212161234c30367)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="boundOrganizationalUnits")
    def bound_organizational_units(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundOrganizationalUnits"))

    @bound_organizational_units.setter
    def bound_organizational_units(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ab53042dc8bc7df5bb8f456245cc15ae6a1eb97305848bd0c0b3063e1b77686)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundOrganizationalUnits", value)

    @builtins.property
    @jsii.member(jsii_name="boundUriSans")
    def bound_uri_sans(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundUriSans"))

    @bound_uri_sans.setter
    def bound_uri_sans(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d64f240795588e5c0b7e5950ce160383e3d35ea392213b159755588526209831)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundUriSans", value)

    @builtins.property
    @jsii.member(jsii_name="certificateData")
    def certificate_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateData"))

    @certificate_data.setter
    def certificate_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__969b8e3b97ea6cf50febb0eba0676c6f7c6a56339403424fddcc6d73118c8c1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateData", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__050ed51769d323bef217ae523a618e70bdc405c08091840ca0dbf74596e5624f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="forceSubClaims")
    def force_sub_claims(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "forceSubClaims"))

    @force_sub_claims.setter
    def force_sub_claims(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6009291d0471d1e4401386c076ae8faed837414a016965b5d632217594bccf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceSubClaims", value)

    @builtins.property
    @jsii.member(jsii_name="gwBoundIps")
    def gw_bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gwBoundIps"))

    @gw_bound_ips.setter
    def gw_bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb1b061c48efe04af99c48153beb553fe1a3590c6f47a12696d3bd8646ab329b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gwBoundIps", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381c1b39730dd28a8d2e941ac9022d7e3a0948c95da814ab88a985f4af38995c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="jwtTtl")
    def jwt_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jwtTtl"))

    @jwt_ttl.setter
    def jwt_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49fecaf2c2064f0c01fbccf12655ac817c0aff766b5b9117fb431dc092e2f20d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtTtl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a9e86a2cebe7d9c8dcaec3779bf0f7e5e83f54db8dfef0ecba2508fd46a007c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="revokedCertIds")
    def revoked_cert_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "revokedCertIds"))

    @revoked_cert_ids.setter
    def revoked_cert_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1154b5b1709ccf0905d1949ac1ea027ff392244dfdeb00fb4df4f05da02ee525)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revokedCertIds", value)

    @builtins.property
    @jsii.member(jsii_name="uniqueIdentifier")
    def unique_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueIdentifier"))

    @unique_identifier.setter
    def unique_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__971ff1e148c82d83dc76cc86ceebdaf9ff762fee8089bae8078b687977fcd23b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uniqueIdentifier", value)


@jsii.data_type(
    jsii_type="akeyless.authMethodCert.AuthMethodCertConfig",
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
        "unique_identifier": "uniqueIdentifier",
        "access_expires": "accessExpires",
        "audit_logs_claims": "auditLogsClaims",
        "bound_common_names": "boundCommonNames",
        "bound_dns_sans": "boundDnsSans",
        "bound_email_sans": "boundEmailSans",
        "bound_extensions": "boundExtensions",
        "bound_ips": "boundIps",
        "bound_organizational_units": "boundOrganizationalUnits",
        "bound_uri_sans": "boundUriSans",
        "certificate_data": "certificateData",
        "delete_protection": "deleteProtection",
        "force_sub_claims": "forceSubClaims",
        "gw_bound_ips": "gwBoundIps",
        "id": "id",
        "jwt_ttl": "jwtTtl",
        "revoked_cert_ids": "revokedCertIds",
    },
)
class AuthMethodCertConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        unique_identifier: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
        certificate_data: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        revoked_cert_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#name AuthMethodCert#name}
        :param unique_identifier: A unique identifier (ID) value should be configured for OIDC, OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#unique_identifier AuthMethodCert#unique_identifier}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#access_expires AuthMethodCert#access_expires}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#audit_logs_claims AuthMethodCert#audit_logs_claims}
        :param bound_common_names: A list of names. At least one must exist in the Common Name. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_common_names AuthMethodCert#bound_common_names}
        :param bound_dns_sans: A list of DNS names. At least one must exist in the SANs. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_dns_sans AuthMethodCert#bound_dns_sans}
        :param bound_email_sans: A list of Email Addresses. At least one must exist in the SANs. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_email_sans AuthMethodCert#bound_email_sans}
        :param bound_extensions: A list of extensions formatted as 'oid:value'. Expects the extension value to be some type of ASN1 encoded string. All values much match. Supports globbing on 'value'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_extensions AuthMethodCert#bound_extensions}
        :param bound_ips: A comma-separated CIDR block list to allow client access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_ips AuthMethodCert#bound_ips}
        :param bound_organizational_units: A list of Organizational Units names. At least one must exist in the OU field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_organizational_units AuthMethodCert#bound_organizational_units}
        :param bound_uri_sans: A list of URIs. At least one must exist in the SANs. Supports globbing. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_uri_sans AuthMethodCert#bound_uri_sans}
        :param certificate_data: The certificate data in base64, if no file was provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#certificate_data AuthMethodCert#certificate_data}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#delete_protection AuthMethodCert#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#force_sub_claims AuthMethodCert#force_sub_claims}
        :param gw_bound_ips: A comma-separated CIDR block list as a trusted Gateway entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#gw_bound_ips AuthMethodCert#gw_bound_ips}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#id AuthMethodCert#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#jwt_ttl AuthMethodCert#jwt_ttl}
        :param revoked_cert_ids: A list of revoked cert ids. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#revoked_cert_ids AuthMethodCert#revoked_cert_ids}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0b7b63663e9da6028939b566eac5cc66fede4a361a84a5c7d407f1cce342cc8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument unique_identifier", value=unique_identifier, expected_type=type_hints["unique_identifier"])
            check_type(argname="argument access_expires", value=access_expires, expected_type=type_hints["access_expires"])
            check_type(argname="argument audit_logs_claims", value=audit_logs_claims, expected_type=type_hints["audit_logs_claims"])
            check_type(argname="argument bound_common_names", value=bound_common_names, expected_type=type_hints["bound_common_names"])
            check_type(argname="argument bound_dns_sans", value=bound_dns_sans, expected_type=type_hints["bound_dns_sans"])
            check_type(argname="argument bound_email_sans", value=bound_email_sans, expected_type=type_hints["bound_email_sans"])
            check_type(argname="argument bound_extensions", value=bound_extensions, expected_type=type_hints["bound_extensions"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument bound_organizational_units", value=bound_organizational_units, expected_type=type_hints["bound_organizational_units"])
            check_type(argname="argument bound_uri_sans", value=bound_uri_sans, expected_type=type_hints["bound_uri_sans"])
            check_type(argname="argument certificate_data", value=certificate_data, expected_type=type_hints["certificate_data"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument force_sub_claims", value=force_sub_claims, expected_type=type_hints["force_sub_claims"])
            check_type(argname="argument gw_bound_ips", value=gw_bound_ips, expected_type=type_hints["gw_bound_ips"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jwt_ttl", value=jwt_ttl, expected_type=type_hints["jwt_ttl"])
            check_type(argname="argument revoked_cert_ids", value=revoked_cert_ids, expected_type=type_hints["revoked_cert_ids"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "unique_identifier": unique_identifier,
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
        if access_expires is not None:
            self._values["access_expires"] = access_expires
        if audit_logs_claims is not None:
            self._values["audit_logs_claims"] = audit_logs_claims
        if bound_common_names is not None:
            self._values["bound_common_names"] = bound_common_names
        if bound_dns_sans is not None:
            self._values["bound_dns_sans"] = bound_dns_sans
        if bound_email_sans is not None:
            self._values["bound_email_sans"] = bound_email_sans
        if bound_extensions is not None:
            self._values["bound_extensions"] = bound_extensions
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if bound_organizational_units is not None:
            self._values["bound_organizational_units"] = bound_organizational_units
        if bound_uri_sans is not None:
            self._values["bound_uri_sans"] = bound_uri_sans
        if certificate_data is not None:
            self._values["certificate_data"] = certificate_data
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if force_sub_claims is not None:
            self._values["force_sub_claims"] = force_sub_claims
        if gw_bound_ips is not None:
            self._values["gw_bound_ips"] = gw_bound_ips
        if id is not None:
            self._values["id"] = id
        if jwt_ttl is not None:
            self._values["jwt_ttl"] = jwt_ttl
        if revoked_cert_ids is not None:
            self._values["revoked_cert_ids"] = revoked_cert_ids

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
        '''Auth Method name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#name AuthMethodCert#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def unique_identifier(self) -> builtins.str:
        '''A unique identifier (ID) value should be configured for OIDC, OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example.

        Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#unique_identifier AuthMethodCert#unique_identifier}
        '''
        result = self._values.get("unique_identifier")
        assert result is not None, "Required property 'unique_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#access_expires AuthMethodCert#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def audit_logs_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Subclaims to include in audit logs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#audit_logs_claims AuthMethodCert#audit_logs_claims}
        '''
        result = self._values.get("audit_logs_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_common_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of names. At least one must exist in the Common Name. Supports globbing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_common_names AuthMethodCert#bound_common_names}
        '''
        result = self._values.get("bound_common_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_dns_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of DNS names. At least one must exist in the SANs. Supports globbing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_dns_sans AuthMethodCert#bound_dns_sans}
        '''
        result = self._values.get("bound_dns_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_email_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of Email Addresses. At least one must exist in the SANs. Supports globbing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_email_sans AuthMethodCert#bound_email_sans}
        '''
        result = self._values.get("bound_email_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_extensions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of extensions formatted as 'oid:value'.

        Expects the extension value to be some type of ASN1 encoded string. All values much match. Supports globbing on 'value'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_extensions AuthMethodCert#bound_extensions}
        '''
        result = self._values.get("bound_extensions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated CIDR block list to allow client access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_ips AuthMethodCert#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_organizational_units(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of Organizational Units names. At least one must exist in the OU field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_organizational_units AuthMethodCert#bound_organizational_units}
        '''
        result = self._values.get("bound_organizational_units")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_uri_sans(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of URIs. At least one must exist in the SANs. Supports globbing.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#bound_uri_sans AuthMethodCert#bound_uri_sans}
        '''
        result = self._values.get("bound_uri_sans")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def certificate_data(self) -> typing.Optional[builtins.str]:
        '''The certificate data in base64, if no file was provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#certificate_data AuthMethodCert#certificate_data}
        '''
        result = self._values.get("certificate_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this auth method, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#delete_protection AuthMethodCert#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_sub_claims(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''enforce role-association must include sub claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#force_sub_claims AuthMethodCert#force_sub_claims}
        '''
        result = self._values.get("force_sub_claims")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gw_bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated CIDR block list as a trusted Gateway entity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#gw_bound_ips AuthMethodCert#gw_bound_ips}
        '''
        result = self._values.get("gw_bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#id AuthMethodCert#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_ttl(self) -> typing.Optional[jsii.Number]:
        '''Creds expiration time in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#jwt_ttl AuthMethodCert#jwt_ttl}
        '''
        result = self._values.get("jwt_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def revoked_cert_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of revoked cert ids.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_cert#revoked_cert_ids AuthMethodCert#revoked_cert_ids}
        '''
        result = self._values.get("revoked_cert_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodCertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthMethodCert",
    "AuthMethodCertConfig",
]

publication.publish()

def _typecheckingstub__ecdad21be499102013f77137326f33474e178c860ef70d2a0bf5c60af900e2bf(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    unique_identifier: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    certificate_data: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    revoked_cert_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__d41424b06e6326add650ecabc4aad5e892ad1e60510a6475bcf3330236a0e772(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2dcdaf13df142f9e3ad48eeb3a33aa6b5122d15cd002b641f74f0753d5ceae57(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7a026bdd8ee53b77b010a50746aaa0b8405e6f39f46088429455a4d165cd3b7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f24de86ced3e57fd7d30bb30663a7638b983f8ee79d55a32224960e79da80301(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4e5f26f73b29bf054754264aecf8214c4fb4a4c7733c3b8b7778b9c9083c460(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9aca1e9e12db2b23effbda69b76afba512a5387000b89d7da9e8ea6152741b58(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25417c6b23fe5927e98631576c7df0ff39355f83ff02882e7bb747b109b6037e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__124d03521013f883ffb944311efc451f2eab4ce6fd24c7126212161234c30367(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ab53042dc8bc7df5bb8f456245cc15ae6a1eb97305848bd0c0b3063e1b77686(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d64f240795588e5c0b7e5950ce160383e3d35ea392213b159755588526209831(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__969b8e3b97ea6cf50febb0eba0676c6f7c6a56339403424fddcc6d73118c8c1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__050ed51769d323bef217ae523a618e70bdc405c08091840ca0dbf74596e5624f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6009291d0471d1e4401386c076ae8faed837414a016965b5d632217594bccf7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb1b061c48efe04af99c48153beb553fe1a3590c6f47a12696d3bd8646ab329b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381c1b39730dd28a8d2e941ac9022d7e3a0948c95da814ab88a985f4af38995c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49fecaf2c2064f0c01fbccf12655ac817c0aff766b5b9117fb431dc092e2f20d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a9e86a2cebe7d9c8dcaec3779bf0f7e5e83f54db8dfef0ecba2508fd46a007c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1154b5b1709ccf0905d1949ac1ea027ff392244dfdeb00fb4df4f05da02ee525(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__971ff1e148c82d83dc76cc86ceebdaf9ff762fee8089bae8078b687977fcd23b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0b7b63663e9da6028939b566eac5cc66fede4a361a84a5c7d407f1cce342cc8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    unique_identifier: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_common_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_dns_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_email_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_extensions: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_organizational_units: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_uri_sans: typing.Optional[typing.Sequence[builtins.str]] = None,
    certificate_data: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    revoked_cert_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
