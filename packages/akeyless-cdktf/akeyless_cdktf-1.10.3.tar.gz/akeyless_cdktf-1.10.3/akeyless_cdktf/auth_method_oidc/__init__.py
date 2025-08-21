'''
# `akeyless_auth_method_oidc`

Refer to the Terraform Registry for docs: [`akeyless_auth_method_oidc`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc).
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


class AuthMethodOidc(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethodOidc.AuthMethodOidc",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc akeyless_auth_method_oidc}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        unique_identifier: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        allowed_redirect_uri: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        required_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        required_scopes_prefix: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc akeyless_auth_method_oidc} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#name AuthMethodOidc#name}
        :param unique_identifier: A unique identifier (ID) value should be configured for OIDC, OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#unique_identifier AuthMethodOidc#unique_identifier}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#access_expires AuthMethodOidc#access_expires}
        :param allowed_redirect_uri: Allowed redirect URIs after the authentication (default is https://console.akeyless.io/login-oidc to enable OIDC via Akeyless Console and http://127.0.0.1:* to enable OIDC via akeyless CLI). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#allowed_redirect_uri AuthMethodOidc#allowed_redirect_uri}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#audit_logs_claims AuthMethodOidc#audit_logs_claims}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#bound_ips AuthMethodOidc#bound_ips}
        :param client_id: Client ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#client_id AuthMethodOidc#client_id}
        :param client_secret: Client Secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#client_secret AuthMethodOidc#client_secret}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#delete_protection AuthMethodOidc#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#force_sub_claims AuthMethodOidc#force_sub_claims}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#id AuthMethodOidc#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#issuer AuthMethodOidc#issuer}
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#jwt_ttl AuthMethodOidc#jwt_ttl}
        :param required_scopes: Required scopes that the oidc method will request from the oidc provider and the user must approve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#required_scopes AuthMethodOidc#required_scopes}
        :param required_scopes_prefix: A prefix to add to all required-scopes when requesting them from the oidc server (for example, azure's Application ID URI). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#required_scopes_prefix AuthMethodOidc#required_scopes_prefix}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__457f59b42a1bd2d0cd34498d0e4fdcad4021325d1f4591c0bcde7e30e547e859)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodOidcConfig(
            name=name,
            unique_identifier=unique_identifier,
            access_expires=access_expires,
            allowed_redirect_uri=allowed_redirect_uri,
            audit_logs_claims=audit_logs_claims,
            bound_ips=bound_ips,
            client_id=client_id,
            client_secret=client_secret,
            delete_protection=delete_protection,
            force_sub_claims=force_sub_claims,
            id=id,
            issuer=issuer,
            jwt_ttl=jwt_ttl,
            required_scopes=required_scopes,
            required_scopes_prefix=required_scopes_prefix,
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
        '''Generates CDKTF code for importing a AuthMethodOidc resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethodOidc to import.
        :param import_from_id: The id of the existing AuthMethodOidc that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethodOidc to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20f521f57475cef48733837a10a3adea7e9eaae2bd0bac6a4ff1224a4a78dbdc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessExpires")
    def reset_access_expires(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessExpires", []))

    @jsii.member(jsii_name="resetAllowedRedirectUri")
    def reset_allowed_redirect_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowedRedirectUri", []))

    @jsii.member(jsii_name="resetAuditLogsClaims")
    def reset_audit_logs_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditLogsClaims", []))

    @jsii.member(jsii_name="resetBoundIps")
    def reset_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIps", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetClientSecret")
    def reset_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientSecret", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetForceSubClaims")
    def reset_force_sub_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceSubClaims", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIssuer")
    def reset_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIssuer", []))

    @jsii.member(jsii_name="resetJwtTtl")
    def reset_jwt_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtTtl", []))

    @jsii.member(jsii_name="resetRequiredScopes")
    def reset_required_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredScopes", []))

    @jsii.member(jsii_name="resetRequiredScopesPrefix")
    def reset_required_scopes_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequiredScopesPrefix", []))

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
    @jsii.member(jsii_name="allowedRedirectUriInput")
    def allowed_redirect_uri_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedRedirectUriInput"))

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaimsInput")
    def audit_logs_claims_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "auditLogsClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIpsInput")
    def bound_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clientSecretInput")
    def client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientSecretInput"))

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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerInput")
    def issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtTtlInput")
    def jwt_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "jwtTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredScopesInput")
    def required_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "requiredScopesInput"))

    @builtins.property
    @jsii.member(jsii_name="requiredScopesPrefixInput")
    def required_scopes_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requiredScopesPrefixInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__bf2fe1dd159f2c72795166ceb344468b56e12dd4fd81451ca11d7602df308511)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="allowedRedirectUri")
    def allowed_redirect_uri(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedRedirectUri"))

    @allowed_redirect_uri.setter
    def allowed_redirect_uri(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71e408043100ed03026625eae954bc4cbfb66d6c91af249181330b11fc3c8833)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedRedirectUri", value)

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaims")
    def audit_logs_claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditLogsClaims"))

    @audit_logs_claims.setter
    def audit_logs_claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e50d380d3c9fffc51dd5df37074e2454c8cc7cca3a6be8279bcec5cb1e873386)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditLogsClaims", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__053cb7958f09234d3b669b6cb37a99590697aac4fe0c5c0b3ea884b04f405c6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09ceda073d107451507a793676b27490afca13606c4fc14bdada6a68a19fc8fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value)

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @client_secret.setter
    def client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f60b2fa6612e0d68fda99e2016ff135d28e8a5e6d977f6b20ceeed8b42226d2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0c7d35059a479e91f7fd2facf6bf7cc81d835facfc59885aaef134aca4fa675)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d04727f13bb9185cc2e820c720f71f3d10bf21fb8b34b21e2cbebd7f764d1c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceSubClaims", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79a4ba06516dfb95a1554b61a124f1f642c11b743a72c940c951ff36f884edc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @issuer.setter
    def issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e035596c5e65fc4a3833c4d1541bd7c2f1470b13b90619cb5c0c7cd08d8f8bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuer", value)

    @builtins.property
    @jsii.member(jsii_name="jwtTtl")
    def jwt_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jwtTtl"))

    @jwt_ttl.setter
    def jwt_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24cc2d2e59fa01f2138fd8072f83646506ca45adbe466df61b0255fb3cdd6d58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtTtl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4740316c55fd6493ff897f5f1e5a180e4880b2bc97818404dcab814f699a82d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="requiredScopes")
    def required_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "requiredScopes"))

    @required_scopes.setter
    def required_scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57416a9a0081bc6fcaa27e25239fc8fc6d6d931e11cb4fb1e06192dbe1e25f07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredScopes", value)

    @builtins.property
    @jsii.member(jsii_name="requiredScopesPrefix")
    def required_scopes_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requiredScopesPrefix"))

    @required_scopes_prefix.setter
    def required_scopes_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f39c1a2cd8d6456d6b3314faad23f87cee2c0939a5a5bc30d9dcd037b77f8cd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requiredScopesPrefix", value)

    @builtins.property
    @jsii.member(jsii_name="uniqueIdentifier")
    def unique_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueIdentifier"))

    @unique_identifier.setter
    def unique_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91e35927d2d51cc34d6ad84d26bc29abc561bcb7da33488202320bad1b69f8c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uniqueIdentifier", value)


@jsii.data_type(
    jsii_type="akeyless.authMethodOidc.AuthMethodOidcConfig",
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
        "allowed_redirect_uri": "allowedRedirectUri",
        "audit_logs_claims": "auditLogsClaims",
        "bound_ips": "boundIps",
        "client_id": "clientId",
        "client_secret": "clientSecret",
        "delete_protection": "deleteProtection",
        "force_sub_claims": "forceSubClaims",
        "id": "id",
        "issuer": "issuer",
        "jwt_ttl": "jwtTtl",
        "required_scopes": "requiredScopes",
        "required_scopes_prefix": "requiredScopesPrefix",
    },
)
class AuthMethodOidcConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_redirect_uri: typing.Optional[typing.Sequence[builtins.str]] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        client_id: typing.Optional[builtins.str] = None,
        client_secret: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        required_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        required_scopes_prefix: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#name AuthMethodOidc#name}
        :param unique_identifier: A unique identifier (ID) value should be configured for OIDC, OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#unique_identifier AuthMethodOidc#unique_identifier}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#access_expires AuthMethodOidc#access_expires}
        :param allowed_redirect_uri: Allowed redirect URIs after the authentication (default is https://console.akeyless.io/login-oidc to enable OIDC via Akeyless Console and http://127.0.0.1:* to enable OIDC via akeyless CLI). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#allowed_redirect_uri AuthMethodOidc#allowed_redirect_uri}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#audit_logs_claims AuthMethodOidc#audit_logs_claims}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#bound_ips AuthMethodOidc#bound_ips}
        :param client_id: Client ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#client_id AuthMethodOidc#client_id}
        :param client_secret: Client Secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#client_secret AuthMethodOidc#client_secret}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#delete_protection AuthMethodOidc#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#force_sub_claims AuthMethodOidc#force_sub_claims}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#id AuthMethodOidc#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#issuer AuthMethodOidc#issuer}
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#jwt_ttl AuthMethodOidc#jwt_ttl}
        :param required_scopes: Required scopes that the oidc method will request from the oidc provider and the user must approve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#required_scopes AuthMethodOidc#required_scopes}
        :param required_scopes_prefix: A prefix to add to all required-scopes when requesting them from the oidc server (for example, azure's Application ID URI). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#required_scopes_prefix AuthMethodOidc#required_scopes_prefix}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbcbcf8fd928c71987e2c1357b369928f0f19b8610b4c5033d7870e921d143d6)
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
            check_type(argname="argument allowed_redirect_uri", value=allowed_redirect_uri, expected_type=type_hints["allowed_redirect_uri"])
            check_type(argname="argument audit_logs_claims", value=audit_logs_claims, expected_type=type_hints["audit_logs_claims"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument client_secret", value=client_secret, expected_type=type_hints["client_secret"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument force_sub_claims", value=force_sub_claims, expected_type=type_hints["force_sub_claims"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument issuer", value=issuer, expected_type=type_hints["issuer"])
            check_type(argname="argument jwt_ttl", value=jwt_ttl, expected_type=type_hints["jwt_ttl"])
            check_type(argname="argument required_scopes", value=required_scopes, expected_type=type_hints["required_scopes"])
            check_type(argname="argument required_scopes_prefix", value=required_scopes_prefix, expected_type=type_hints["required_scopes_prefix"])
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
        if allowed_redirect_uri is not None:
            self._values["allowed_redirect_uri"] = allowed_redirect_uri
        if audit_logs_claims is not None:
            self._values["audit_logs_claims"] = audit_logs_claims
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if client_id is not None:
            self._values["client_id"] = client_id
        if client_secret is not None:
            self._values["client_secret"] = client_secret
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if force_sub_claims is not None:
            self._values["force_sub_claims"] = force_sub_claims
        if id is not None:
            self._values["id"] = id
        if issuer is not None:
            self._values["issuer"] = issuer
        if jwt_ttl is not None:
            self._values["jwt_ttl"] = jwt_ttl
        if required_scopes is not None:
            self._values["required_scopes"] = required_scopes
        if required_scopes_prefix is not None:
            self._values["required_scopes_prefix"] = required_scopes_prefix

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#name AuthMethodOidc#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def unique_identifier(self) -> builtins.str:
        '''A unique identifier (ID) value should be configured for OIDC, OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example.

        Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#unique_identifier AuthMethodOidc#unique_identifier}
        '''
        result = self._values.get("unique_identifier")
        assert result is not None, "Required property 'unique_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#access_expires AuthMethodOidc#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def allowed_redirect_uri(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Allowed redirect URIs after the authentication (default is https://console.akeyless.io/login-oidc to enable OIDC via Akeyless Console and  http://127.0.0.1:* to enable OIDC via akeyless CLI).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#allowed_redirect_uri AuthMethodOidc#allowed_redirect_uri}
        '''
        result = self._values.get("allowed_redirect_uri")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audit_logs_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Subclaims to include in audit logs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#audit_logs_claims AuthMethodOidc#audit_logs_claims}
        '''
        result = self._values.get("audit_logs_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A CIDR whitelist with the IPs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#bound_ips AuthMethodOidc#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Client ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#client_id AuthMethodOidc#client_id}
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_secret(self) -> typing.Optional[builtins.str]:
        '''Client Secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#client_secret AuthMethodOidc#client_secret}
        '''
        result = self._values.get("client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this auth method, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#delete_protection AuthMethodOidc#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_sub_claims(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''enforce role-association must include sub claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#force_sub_claims AuthMethodOidc#force_sub_claims}
        '''
        result = self._values.get("force_sub_claims")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#id AuthMethodOidc#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issuer(self) -> typing.Optional[builtins.str]:
        '''Issuer URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#issuer AuthMethodOidc#issuer}
        '''
        result = self._values.get("issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_ttl(self) -> typing.Optional[jsii.Number]:
        '''Creds expiration time in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#jwt_ttl AuthMethodOidc#jwt_ttl}
        '''
        result = self._values.get("jwt_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def required_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Required scopes that the oidc method will request from the oidc provider and the user must approve.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#required_scopes AuthMethodOidc#required_scopes}
        '''
        result = self._values.get("required_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def required_scopes_prefix(self) -> typing.Optional[builtins.str]:
        '''A prefix to add to all required-scopes when requesting them from the oidc server (for example, azure's Application ID URI).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_oidc#required_scopes_prefix AuthMethodOidc#required_scopes_prefix}
        '''
        result = self._values.get("required_scopes_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodOidcConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthMethodOidc",
    "AuthMethodOidcConfig",
]

publication.publish()

def _typecheckingstub__457f59b42a1bd2d0cd34498d0e4fdcad4021325d1f4591c0bcde7e30e547e859(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    unique_identifier: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    allowed_redirect_uri: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    required_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    required_scopes_prefix: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__20f521f57475cef48733837a10a3adea7e9eaae2bd0bac6a4ff1224a4a78dbdc(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf2fe1dd159f2c72795166ceb344468b56e12dd4fd81451ca11d7602df308511(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71e408043100ed03026625eae954bc4cbfb66d6c91af249181330b11fc3c8833(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e50d380d3c9fffc51dd5df37074e2454c8cc7cca3a6be8279bcec5cb1e873386(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__053cb7958f09234d3b669b6cb37a99590697aac4fe0c5c0b3ea884b04f405c6b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09ceda073d107451507a793676b27490afca13606c4fc14bdada6a68a19fc8fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f60b2fa6612e0d68fda99e2016ff135d28e8a5e6d977f6b20ceeed8b42226d2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0c7d35059a479e91f7fd2facf6bf7cc81d835facfc59885aaef134aca4fa675(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d04727f13bb9185cc2e820c720f71f3d10bf21fb8b34b21e2cbebd7f764d1c6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a4ba06516dfb95a1554b61a124f1f642c11b743a72c940c951ff36f884edc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e035596c5e65fc4a3833c4d1541bd7c2f1470b13b90619cb5c0c7cd08d8f8bd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24cc2d2e59fa01f2138fd8072f83646506ca45adbe466df61b0255fb3cdd6d58(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4740316c55fd6493ff897f5f1e5a180e4880b2bc97818404dcab814f699a82d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57416a9a0081bc6fcaa27e25239fc8fc6d6d931e11cb4fb1e06192dbe1e25f07(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f39c1a2cd8d6456d6b3314faad23f87cee2c0939a5a5bc30d9dcd037b77f8cd0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91e35927d2d51cc34d6ad84d26bc29abc561bcb7da33488202320bad1b69f8c9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbcbcf8fd928c71987e2c1357b369928f0f19b8610b4c5033d7870e921d143d6(
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
    allowed_redirect_uri: typing.Optional[typing.Sequence[builtins.str]] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    client_id: typing.Optional[builtins.str] = None,
    client_secret: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    required_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    required_scopes_prefix: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
