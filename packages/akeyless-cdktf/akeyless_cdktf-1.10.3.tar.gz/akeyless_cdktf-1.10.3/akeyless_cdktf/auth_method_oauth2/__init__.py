'''
# `akeyless_auth_method_oauth2`

Refer to the Terraform Registry for docs: [`akeyless_auth_method_oauth2`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2).
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


class AuthMethodOauth2(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethodOauth2.AuthMethodOauth2",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2 akeyless_auth_method_oauth2}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        unique_identifier: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_client_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gateway_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
        jwks_json_data: typing.Optional[builtins.str] = None,
        jwks_uri: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2 akeyless_auth_method_oauth2} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#name AuthMethodOauth2#name}
        :param unique_identifier: A unique identifier (ID) value should be configured for OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#unique_identifier AuthMethodOauth2#unique_identifier}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#access_expires AuthMethodOauth2#access_expires}
        :param audience: The audience in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#audience AuthMethodOauth2#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#audit_logs_claims AuthMethodOauth2#audit_logs_claims}
        :param bound_client_ids: The clients ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#bound_client_ids AuthMethodOauth2#bound_client_ids}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#bound_ips AuthMethodOauth2#bound_ips}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#delete_protection AuthMethodOauth2#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#force_sub_claims AuthMethodOauth2#force_sub_claims}
        :param gateway_url: Akeyless Gateway URL (Configuration Management port). Relevant only when the jwks-uri is accessible only from the gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#gateway_url AuthMethodOauth2#gateway_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#id AuthMethodOauth2#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#issuer AuthMethodOauth2#issuer}
        :param jwks_json_data: The JSON Web Key Set (JWKS) containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization serve, in base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwks_json_data AuthMethodOauth2#jwks_json_data}
        :param jwks_uri: The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwks_uri AuthMethodOauth2#jwks_uri}
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwt_ttl AuthMethodOauth2#jwt_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b593bd6d6df3808e83d6e18417c60b409abbe9932e73fca416f42628a0d8e99b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodOauth2Config(
            name=name,
            unique_identifier=unique_identifier,
            access_expires=access_expires,
            audience=audience,
            audit_logs_claims=audit_logs_claims,
            bound_client_ids=bound_client_ids,
            bound_ips=bound_ips,
            delete_protection=delete_protection,
            force_sub_claims=force_sub_claims,
            gateway_url=gateway_url,
            id=id,
            issuer=issuer,
            jwks_json_data=jwks_json_data,
            jwks_uri=jwks_uri,
            jwt_ttl=jwt_ttl,
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
        '''Generates CDKTF code for importing a AuthMethodOauth2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethodOauth2 to import.
        :param import_from_id: The id of the existing AuthMethodOauth2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethodOauth2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9db9b9bb6e2e8645283e6f577d19271e66cafdf32bebc4ab0abea4e6912920a2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessExpires")
    def reset_access_expires(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessExpires", []))

    @jsii.member(jsii_name="resetAudience")
    def reset_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudience", []))

    @jsii.member(jsii_name="resetAuditLogsClaims")
    def reset_audit_logs_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditLogsClaims", []))

    @jsii.member(jsii_name="resetBoundClientIds")
    def reset_bound_client_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundClientIds", []))

    @jsii.member(jsii_name="resetBoundIps")
    def reset_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIps", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetForceSubClaims")
    def reset_force_sub_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceSubClaims", []))

    @jsii.member(jsii_name="resetGatewayUrl")
    def reset_gateway_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGatewayUrl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIssuer")
    def reset_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuer", []))

    @jsii.member(jsii_name="resetJwksJsonData")
    def reset_jwks_json_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksJsonData", []))

    @jsii.member(jsii_name="resetJwksUri")
    def reset_jwks_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksUri", []))

    @jsii.member(jsii_name="resetJwtTtl")
    def reset_jwt_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtTtl", []))

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
    @jsii.member(jsii_name="audienceInput")
    def audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audienceInput"))

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaimsInput")
    def audit_logs_claims_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "auditLogsClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundClientIdsInput")
    def bound_client_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundClientIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIpsInput")
    def bound_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundIpsInput"))

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
    @jsii.member(jsii_name="gatewayUrlInput")
    def gateway_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gatewayUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerInput")
    def issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksJsonDataInput")
    def jwks_json_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwksJsonDataInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksUriInput")
    def jwks_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwksUriInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtTtlInput")
    def jwt_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "jwtTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__93a33d4d7afd682320f1caca7bfdbec091bc5c4b191c054cbfb0c1ca7cf61407)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c316d75fcede8db744d391bbdcb8be35f72c6db0a7041b75b1592c7faf78d6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value)

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaims")
    def audit_logs_claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditLogsClaims"))

    @audit_logs_claims.setter
    def audit_logs_claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2417a9d8d3d6e212a43efb28238431e3ef0e1ff55c2749dc1ad6b1dab134a6a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditLogsClaims", value)

    @builtins.property
    @jsii.member(jsii_name="boundClientIds")
    def bound_client_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundClientIds"))

    @bound_client_ids.setter
    def bound_client_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8b43f584ee0217cc696dae37a940b667749ce6b027a5b7ffbbe56a000132b73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundClientIds", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e3b7d2f346ab2d0d0cc8db5f1ca74c6f9fbaabbda77d2f50f795b5b12f2f1fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85d873e879f424931f48a31c65896fd7399498ec085b024ee56a0cf4b69499ef)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0393672f2d5c7a1c4e8edfe6a23e9209a98672a78aa978f77a94f9b00e9546e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceSubClaims", value)

    @builtins.property
    @jsii.member(jsii_name="gatewayUrl")
    def gateway_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gatewayUrl"))

    @gateway_url.setter
    def gateway_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c4d53e5a8fbaa3148ae5385a8f332bf9c920eab5f6230467579f71c38fa6c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gatewayUrl", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07592d3aeff76c9f35680399e4c12a2195b813a93392b67c75e3be26343b2d61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @issuer.setter
    def issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ca017171d2b3a7dfca1a1c921ad70cf54b0ebbc2f73a221908609d3724ea9d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuer", value)

    @builtins.property
    @jsii.member(jsii_name="jwksJsonData")
    def jwks_json_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksJsonData"))

    @jwks_json_data.setter
    def jwks_json_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfdb0a7d5e96bc9af464497f8798004d5959d6056bb62db3a67e147edc7770ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksJsonData", value)

    @builtins.property
    @jsii.member(jsii_name="jwksUri")
    def jwks_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksUri"))

    @jwks_uri.setter
    def jwks_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0513fb43ca75f9decb7f25a63edf6a2686ada3b78998825ba5a24f336cf1a668)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksUri", value)

    @builtins.property
    @jsii.member(jsii_name="jwtTtl")
    def jwt_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jwtTtl"))

    @jwt_ttl.setter
    def jwt_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29828ad9f2d8911cbff1438333f0a632dcb366e5ca3c1ce3b2744dcc99881a6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtTtl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2146dd09d9f741cf04ee7fc9bb9d8c8a01b518040bb1abe69eb17dab5ee369bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="uniqueIdentifier")
    def unique_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueIdentifier"))

    @unique_identifier.setter
    def unique_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c279679c15b40923aeefa0d2aeff18d038c59ffae21f94a82414bbd5c5295be1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uniqueIdentifier", value)


@jsii.data_type(
    jsii_type="akeyless.authMethodOauth2.AuthMethodOauth2Config",
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
        "audience": "audience",
        "audit_logs_claims": "auditLogsClaims",
        "bound_client_ids": "boundClientIds",
        "bound_ips": "boundIps",
        "delete_protection": "deleteProtection",
        "force_sub_claims": "forceSubClaims",
        "gateway_url": "gatewayUrl",
        "id": "id",
        "issuer": "issuer",
        "jwks_json_data": "jwksJsonData",
        "jwks_uri": "jwksUri",
        "jwt_ttl": "jwtTtl",
    },
)
class AuthMethodOauth2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_client_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gateway_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
        jwks_json_data: typing.Optional[builtins.str] = None,
        jwks_uri: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#name AuthMethodOauth2#name}
        :param unique_identifier: A unique identifier (ID) value should be configured for OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#unique_identifier AuthMethodOauth2#unique_identifier}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#access_expires AuthMethodOauth2#access_expires}
        :param audience: The audience in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#audience AuthMethodOauth2#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#audit_logs_claims AuthMethodOauth2#audit_logs_claims}
        :param bound_client_ids: The clients ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#bound_client_ids AuthMethodOauth2#bound_client_ids}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#bound_ips AuthMethodOauth2#bound_ips}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#delete_protection AuthMethodOauth2#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#force_sub_claims AuthMethodOauth2#force_sub_claims}
        :param gateway_url: Akeyless Gateway URL (Configuration Management port). Relevant only when the jwks-uri is accessible only from the gateway. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#gateway_url AuthMethodOauth2#gateway_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#id AuthMethodOauth2#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#issuer AuthMethodOauth2#issuer}
        :param jwks_json_data: The JSON Web Key Set (JWKS) containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization serve, in base64 format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwks_json_data AuthMethodOauth2#jwks_json_data}
        :param jwks_uri: The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwks_uri AuthMethodOauth2#jwks_uri}
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwt_ttl AuthMethodOauth2#jwt_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c373068f466d767fc2e9d43efc350aa152fbb79d5ae27e1744dabd8fac9a337e)
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
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument audit_logs_claims", value=audit_logs_claims, expected_type=type_hints["audit_logs_claims"])
            check_type(argname="argument bound_client_ids", value=bound_client_ids, expected_type=type_hints["bound_client_ids"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument force_sub_claims", value=force_sub_claims, expected_type=type_hints["force_sub_claims"])
            check_type(argname="argument gateway_url", value=gateway_url, expected_type=type_hints["gateway_url"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument issuer", value=issuer, expected_type=type_hints["issuer"])
            check_type(argname="argument jwks_json_data", value=jwks_json_data, expected_type=type_hints["jwks_json_data"])
            check_type(argname="argument jwks_uri", value=jwks_uri, expected_type=type_hints["jwks_uri"])
            check_type(argname="argument jwt_ttl", value=jwt_ttl, expected_type=type_hints["jwt_ttl"])
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
        if audience is not None:
            self._values["audience"] = audience
        if audit_logs_claims is not None:
            self._values["audit_logs_claims"] = audit_logs_claims
        if bound_client_ids is not None:
            self._values["bound_client_ids"] = bound_client_ids
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if force_sub_claims is not None:
            self._values["force_sub_claims"] = force_sub_claims
        if gateway_url is not None:
            self._values["gateway_url"] = gateway_url
        if id is not None:
            self._values["id"] = id
        if issuer is not None:
            self._values["issuer"] = issuer
        if jwks_json_data is not None:
            self._values["jwks_json_data"] = jwks_json_data
        if jwks_uri is not None:
            self._values["jwks_uri"] = jwks_uri
        if jwt_ttl is not None:
            self._values["jwt_ttl"] = jwt_ttl

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#name AuthMethodOauth2#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def unique_identifier(self) -> builtins.str:
        '''A unique identifier (ID) value should be configured for OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example.

        Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#unique_identifier AuthMethodOauth2#unique_identifier}
        '''
        result = self._values.get("unique_identifier")
        assert result is not None, "Required property 'unique_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#access_expires AuthMethodOauth2#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''The audience in the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#audience AuthMethodOauth2#audience}
        '''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def audit_logs_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Subclaims to include in audit logs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#audit_logs_claims AuthMethodOauth2#audit_logs_claims}
        '''
        result = self._values.get("audit_logs_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_client_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The clients ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#bound_client_ids AuthMethodOauth2#bound_client_ids}
        '''
        result = self._values.get("bound_client_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A CIDR whitelist with the IPs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#bound_ips AuthMethodOauth2#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this auth method, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#delete_protection AuthMethodOauth2#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_sub_claims(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''enforce role-association must include sub claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#force_sub_claims AuthMethodOauth2#force_sub_claims}
        '''
        result = self._values.get("force_sub_claims")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gateway_url(self) -> typing.Optional[builtins.str]:
        '''Akeyless Gateway URL (Configuration Management port). Relevant only when the jwks-uri is accessible only from the gateway.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#gateway_url AuthMethodOauth2#gateway_url}
        '''
        result = self._values.get("gateway_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#id AuthMethodOauth2#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issuer(self) -> typing.Optional[builtins.str]:
        '''Issuer URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#issuer AuthMethodOauth2#issuer}
        '''
        result = self._values.get("issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_json_data(self) -> typing.Optional[builtins.str]:
        '''The JSON Web Key Set (JWKS) containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization serve, in base64 format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwks_json_data AuthMethodOauth2#jwks_json_data}
        '''
        result = self._values.get("jwks_json_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_uri(self) -> typing.Optional[builtins.str]:
        '''The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwks_uri AuthMethodOauth2#jwks_uri}
        '''
        result = self._values.get("jwks_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_ttl(self) -> typing.Optional[jsii.Number]:
        '''Creds expiration time in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oauth2#jwt_ttl AuthMethodOauth2#jwt_ttl}
        '''
        result = self._values.get("jwt_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodOauth2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthMethodOauth2",
    "AuthMethodOauth2Config",
]

publication.publish()

def _typecheckingstub__b593bd6d6df3808e83d6e18417c60b409abbe9932e73fca416f42628a0d8e99b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    unique_identifier: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_client_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gateway_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
    jwks_json_data: typing.Optional[builtins.str] = None,
    jwks_uri: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__9db9b9bb6e2e8645283e6f577d19271e66cafdf32bebc4ab0abea4e6912920a2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93a33d4d7afd682320f1caca7bfdbec091bc5c4b191c054cbfb0c1ca7cf61407(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c316d75fcede8db744d391bbdcb8be35f72c6db0a7041b75b1592c7faf78d6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2417a9d8d3d6e212a43efb28238431e3ef0e1ff55c2749dc1ad6b1dab134a6a4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b43f584ee0217cc696dae37a940b667749ce6b027a5b7ffbbe56a000132b73(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e3b7d2f346ab2d0d0cc8db5f1ca74c6f9fbaabbda77d2f50f795b5b12f2f1fc(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85d873e879f424931f48a31c65896fd7399498ec085b024ee56a0cf4b69499ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0393672f2d5c7a1c4e8edfe6a23e9209a98672a78aa978f77a94f9b00e9546e9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c4d53e5a8fbaa3148ae5385a8f332bf9c920eab5f6230467579f71c38fa6c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07592d3aeff76c9f35680399e4c12a2195b813a93392b67c75e3be26343b2d61(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ca017171d2b3a7dfca1a1c921ad70cf54b0ebbc2f73a221908609d3724ea9d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfdb0a7d5e96bc9af464497f8798004d5959d6056bb62db3a67e147edc7770ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0513fb43ca75f9decb7f25a63edf6a2686ada3b78998825ba5a24f336cf1a668(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29828ad9f2d8911cbff1438333f0a632dcb366e5ca3c1ce3b2744dcc99881a6e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2146dd09d9f741cf04ee7fc9bb9d8c8a01b518040bb1abe69eb17dab5ee369bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c279679c15b40923aeefa0d2aeff18d038c59ffae21f94a82414bbd5c5295be1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c373068f466d767fc2e9d43efc350aa152fbb79d5ae27e1744dabd8fac9a337e(
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
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_client_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gateway_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
    jwks_json_data: typing.Optional[builtins.str] = None,
    jwks_uri: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
