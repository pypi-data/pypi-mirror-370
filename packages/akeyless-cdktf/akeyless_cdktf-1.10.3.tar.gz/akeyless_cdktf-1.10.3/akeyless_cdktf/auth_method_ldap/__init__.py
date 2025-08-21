'''
# `akeyless_auth_method_ldap`

Refer to the Terraform Registry for docs: [`akeyless_auth_method_ldap`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap).
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


class AuthMethodLdap(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethodLdap.AuthMethodLdap",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap akeyless_auth_method_ldap}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gen_key: typing.Optional[builtins.str] = None,
        gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        product_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        public_key_data: typing.Optional[builtins.str] = None,
        unique_identifier: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap akeyless_auth_method_ldap} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#name AuthMethodLdap#name}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#access_expires AuthMethodLdap#access_expires}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#audit_logs_claims AuthMethodLdap#audit_logs_claims}
        :param bound_ips: A comma-separated CIDR block list to allow client access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#bound_ips AuthMethodLdap#bound_ips}
        :param delete_protection: Protection from accidental deletion of this object, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#delete_protection AuthMethodLdap#delete_protection}
        :param description: Auth Method description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#description AuthMethodLdap#description}
        :param expiration_event_in: How many days before the expiration of the auth method would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#expiration_event_in AuthMethodLdap#expiration_event_in}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#force_sub_claims AuthMethodLdap#force_sub_claims}
        :param gen_key: Automatically generate key-pair for LDAP configuration. If set to false, a public key needs to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#gen_key AuthMethodLdap#gen_key}
        :param gw_bound_ips: A comma-separated CIDR block list as a trusted Gateway entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#gw_bound_ips AuthMethodLdap#gw_bound_ips}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#id AuthMethodLdap#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: creds expiration time in minutes. If not set, use default according to account settings (see get-account-settings). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#jwt_ttl AuthMethodLdap#jwt_ttl}
        :param product_type: Choose the relevant product type for the auth method [sm, sra, pm, dp, ca]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#product_type AuthMethodLdap#product_type}
        :param public_key_data: A public key generated for LDAP authentication method on Akeyless [RSA2048] in Base64 or PEM format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#public_key_data AuthMethodLdap#public_key_data}
        :param unique_identifier: A unique identifier (ID) value should be configured for LDAP, OAuth2 and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#unique_identifier AuthMethodLdap#unique_identifier}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8447d519ec7ea867676e6f52d68543c75dd59f8f946affb48ad4428420473a0d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodLdapConfig(
            name=name,
            access_expires=access_expires,
            audit_logs_claims=audit_logs_claims,
            bound_ips=bound_ips,
            delete_protection=delete_protection,
            description=description,
            expiration_event_in=expiration_event_in,
            force_sub_claims=force_sub_claims,
            gen_key=gen_key,
            gw_bound_ips=gw_bound_ips,
            id=id,
            jwt_ttl=jwt_ttl,
            product_type=product_type,
            public_key_data=public_key_data,
            unique_identifier=unique_identifier,
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
        '''Generates CDKTF code for importing a AuthMethodLdap resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethodLdap to import.
        :param import_from_id: The id of the existing AuthMethodLdap that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethodLdap to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89a84d5c0d01345a9851535fccb6d6424aa7807a7be851065edd131aff3a7698)
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

    @jsii.member(jsii_name="resetBoundIps")
    def reset_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIps", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExpirationEventIn")
    def reset_expiration_event_in(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpirationEventIn", []))

    @jsii.member(jsii_name="resetForceSubClaims")
    def reset_force_sub_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceSubClaims", []))

    @jsii.member(jsii_name="resetGenKey")
    def reset_gen_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenKey", []))

    @jsii.member(jsii_name="resetGwBoundIps")
    def reset_gw_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGwBoundIps", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJwtTtl")
    def reset_jwt_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtTtl", []))

    @jsii.member(jsii_name="resetProductType")
    def reset_product_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProductType", []))

    @jsii.member(jsii_name="resetPublicKeyData")
    def reset_public_key_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicKeyData", []))

    @jsii.member(jsii_name="resetUniqueIdentifier")
    def reset_unique_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUniqueIdentifier", []))

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
    @jsii.member(jsii_name="privateKeyData")
    def private_key_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyData"))

    @builtins.property
    @jsii.member(jsii_name="accessExpiresInput")
    def access_expires_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessExpiresInput"))

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaimsInput")
    def audit_logs_claims_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "auditLogsClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIpsInput")
    def bound_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundIpsInput"))

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
    @jsii.member(jsii_name="forceSubClaimsInput")
    def force_sub_claims_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "forceSubClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="genKeyInput")
    def gen_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "genKeyInput"))

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
    @jsii.member(jsii_name="productTypeInput")
    def product_type_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "productTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="publicKeyDataInput")
    def public_key_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyDataInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2a6524c487e256aa5ade55aa63031df8b6bab1bedbcb98a5fda700b59d5a39bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaims")
    def audit_logs_claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditLogsClaims"))

    @audit_logs_claims.setter
    def audit_logs_claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe0e280fb2ae88434b2f289d056bc9df03138ec16c7bf0ab3c886b9f724d7866)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditLogsClaims", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f596a59670a024842c8b6bf85fb90d757212786265fc745b341cd52e37b36974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6775b820e2e010ed505c2c056bb183d562860056c0200343b5560c6fd97d3f37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8c8f84ed420baeeef25229db98d94a86d5691efd65c3a1382fde6135d82f919)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="expirationEventIn")
    def expiration_event_in(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "expirationEventIn"))

    @expiration_event_in.setter
    def expiration_event_in(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7fde5e7dd448277a23be0c270362275f34dfee9a2e14a7e24e5a606be396e42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationEventIn", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__1c7c52fb208ccc0ac79a89554245d4cfb25dfbfdac0ddfd0bc104b53851fa519)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceSubClaims", value)

    @builtins.property
    @jsii.member(jsii_name="genKey")
    def gen_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "genKey"))

    @gen_key.setter
    def gen_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39d799fc927b238ffdf322967a8d2fb3e8f45cb86ced165341a387f180786368)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "genKey", value)

    @builtins.property
    @jsii.member(jsii_name="gwBoundIps")
    def gw_bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "gwBoundIps"))

    @gw_bound_ips.setter
    def gw_bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0aa95e592dad1584971b3f5411a0efa40cbb79a50569a626c5e68f8e1701286e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gwBoundIps", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52e3205927ee02d69073c729342f105dced49f239aa4e6d508ca7d66e3750eae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="jwtTtl")
    def jwt_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jwtTtl"))

    @jwt_ttl.setter
    def jwt_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11cdfa6355321d4c6032b728fc521e0c2453ad01c4c3da03559a4d2de5e172e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtTtl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__296cde6532523f69511457cdc26337332c9fd8c46e3f5d607a55b2e2e1b50020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="productType")
    def product_type(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "productType"))

    @product_type.setter
    def product_type(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2338310dc30a755fe763c03c2d8674a1f786fd27afc4a739e99a04c2f2fbf326)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "productType", value)

    @builtins.property
    @jsii.member(jsii_name="publicKeyData")
    def public_key_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyData"))

    @public_key_data.setter
    def public_key_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4062e03c7672018507387dbc7e2fae902dfd747117b8136282b23026849d962c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicKeyData", value)

    @builtins.property
    @jsii.member(jsii_name="uniqueIdentifier")
    def unique_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueIdentifier"))

    @unique_identifier.setter
    def unique_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7affee528421f8487df3d52f0ce8919a33b8cfba58663674a9a8e37b695d0c4c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uniqueIdentifier", value)


@jsii.data_type(
    jsii_type="akeyless.authMethodLdap.AuthMethodLdapConfig",
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
        "access_expires": "accessExpires",
        "audit_logs_claims": "auditLogsClaims",
        "bound_ips": "boundIps",
        "delete_protection": "deleteProtection",
        "description": "description",
        "expiration_event_in": "expirationEventIn",
        "force_sub_claims": "forceSubClaims",
        "gen_key": "genKey",
        "gw_bound_ips": "gwBoundIps",
        "id": "id",
        "jwt_ttl": "jwtTtl",
        "product_type": "productType",
        "public_key_data": "publicKeyData",
        "unique_identifier": "uniqueIdentifier",
    },
)
class AuthMethodLdapConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_expires: typing.Optional[jsii.Number] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gen_key: typing.Optional[builtins.str] = None,
        gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        product_type: typing.Optional[typing.Sequence[builtins.str]] = None,
        public_key_data: typing.Optional[builtins.str] = None,
        unique_identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#name AuthMethodLdap#name}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#access_expires AuthMethodLdap#access_expires}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#audit_logs_claims AuthMethodLdap#audit_logs_claims}
        :param bound_ips: A comma-separated CIDR block list to allow client access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#bound_ips AuthMethodLdap#bound_ips}
        :param delete_protection: Protection from accidental deletion of this object, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#delete_protection AuthMethodLdap#delete_protection}
        :param description: Auth Method description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#description AuthMethodLdap#description}
        :param expiration_event_in: How many days before the expiration of the auth method would you like to be notified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#expiration_event_in AuthMethodLdap#expiration_event_in}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#force_sub_claims AuthMethodLdap#force_sub_claims}
        :param gen_key: Automatically generate key-pair for LDAP configuration. If set to false, a public key needs to be provided. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#gen_key AuthMethodLdap#gen_key}
        :param gw_bound_ips: A comma-separated CIDR block list as a trusted Gateway entity. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#gw_bound_ips AuthMethodLdap#gw_bound_ips}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#id AuthMethodLdap#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: creds expiration time in minutes. If not set, use default according to account settings (see get-account-settings). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#jwt_ttl AuthMethodLdap#jwt_ttl}
        :param product_type: Choose the relevant product type for the auth method [sm, sra, pm, dp, ca]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#product_type AuthMethodLdap#product_type}
        :param public_key_data: A public key generated for LDAP authentication method on Akeyless [RSA2048] in Base64 or PEM format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#public_key_data AuthMethodLdap#public_key_data}
        :param unique_identifier: A unique identifier (ID) value should be configured for LDAP, OAuth2 and SAML authentication method types and is usually a value such as the email, username, or upn for example. Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#unique_identifier AuthMethodLdap#unique_identifier}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84a6a4b30af63554027381bf6c01198dc6d31a9d438362851b49f4445380ad1c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument access_expires", value=access_expires, expected_type=type_hints["access_expires"])
            check_type(argname="argument audit_logs_claims", value=audit_logs_claims, expected_type=type_hints["audit_logs_claims"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument expiration_event_in", value=expiration_event_in, expected_type=type_hints["expiration_event_in"])
            check_type(argname="argument force_sub_claims", value=force_sub_claims, expected_type=type_hints["force_sub_claims"])
            check_type(argname="argument gen_key", value=gen_key, expected_type=type_hints["gen_key"])
            check_type(argname="argument gw_bound_ips", value=gw_bound_ips, expected_type=type_hints["gw_bound_ips"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jwt_ttl", value=jwt_ttl, expected_type=type_hints["jwt_ttl"])
            check_type(argname="argument product_type", value=product_type, expected_type=type_hints["product_type"])
            check_type(argname="argument public_key_data", value=public_key_data, expected_type=type_hints["public_key_data"])
            check_type(argname="argument unique_identifier", value=unique_identifier, expected_type=type_hints["unique_identifier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if access_expires is not None:
            self._values["access_expires"] = access_expires
        if audit_logs_claims is not None:
            self._values["audit_logs_claims"] = audit_logs_claims
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if expiration_event_in is not None:
            self._values["expiration_event_in"] = expiration_event_in
        if force_sub_claims is not None:
            self._values["force_sub_claims"] = force_sub_claims
        if gen_key is not None:
            self._values["gen_key"] = gen_key
        if gw_bound_ips is not None:
            self._values["gw_bound_ips"] = gw_bound_ips
        if id is not None:
            self._values["id"] = id
        if jwt_ttl is not None:
            self._values["jwt_ttl"] = jwt_ttl
        if product_type is not None:
            self._values["product_type"] = product_type
        if public_key_data is not None:
            self._values["public_key_data"] = public_key_data
        if unique_identifier is not None:
            self._values["unique_identifier"] = unique_identifier

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#name AuthMethodLdap#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#access_expires AuthMethodLdap#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def audit_logs_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Subclaims to include in audit logs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#audit_logs_claims AuthMethodLdap#audit_logs_claims}
        '''
        result = self._values.get("audit_logs_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated CIDR block list to allow client access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#bound_ips AuthMethodLdap#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this object, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#delete_protection AuthMethodLdap#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Auth Method description.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#description AuthMethodLdap#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expiration_event_in(self) -> typing.Optional[typing.List[builtins.str]]:
        '''How many days before the expiration of the auth method would you like to be notified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#expiration_event_in AuthMethodLdap#expiration_event_in}
        '''
        result = self._values.get("expiration_event_in")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def force_sub_claims(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''enforce role-association must include sub claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#force_sub_claims AuthMethodLdap#force_sub_claims}
        '''
        result = self._values.get("force_sub_claims")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gen_key(self) -> typing.Optional[builtins.str]:
        '''Automatically generate key-pair for LDAP configuration. If set to false, a public key needs to be provided.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#gen_key AuthMethodLdap#gen_key}
        '''
        result = self._values.get("gen_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gw_bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated CIDR block list as a trusted Gateway entity.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#gw_bound_ips AuthMethodLdap#gw_bound_ips}
        '''
        result = self._values.get("gw_bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#id AuthMethodLdap#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_ttl(self) -> typing.Optional[jsii.Number]:
        '''creds expiration time in minutes. If not set, use default according to account settings (see get-account-settings).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#jwt_ttl AuthMethodLdap#jwt_ttl}
        '''
        result = self._values.get("jwt_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def product_type(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Choose the relevant product type for the auth method [sm, sra, pm, dp, ca].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#product_type AuthMethodLdap#product_type}
        '''
        result = self._values.get("product_type")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def public_key_data(self) -> typing.Optional[builtins.str]:
        '''A public key generated for LDAP authentication method on Akeyless [RSA2048] in Base64 or PEM format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#public_key_data AuthMethodLdap#public_key_data}
        '''
        result = self._values.get("public_key_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unique_identifier(self) -> typing.Optional[builtins.str]:
        '''A unique identifier (ID) value should be configured for LDAP, OAuth2 and SAML authentication method types and is usually a value such as the email, username, or upn for example.

        Whenever a user logs in with a token, these authentication types issue a sub claim that contains details uniquely identifying that user. This sub claim includes a key containing the ID value that you configured, and is used to distinguish between different users from within the same organization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_ldap#unique_identifier AuthMethodLdap#unique_identifier}
        '''
        result = self._values.get("unique_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodLdapConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthMethodLdap",
    "AuthMethodLdapConfig",
]

publication.publish()

def _typecheckingstub__8447d519ec7ea867676e6f52d68543c75dd59f8f946affb48ad4428420473a0d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gen_key: typing.Optional[builtins.str] = None,
    gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    product_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    public_key_data: typing.Optional[builtins.str] = None,
    unique_identifier: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__89a84d5c0d01345a9851535fccb6d6424aa7807a7be851065edd131aff3a7698(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a6524c487e256aa5ade55aa63031df8b6bab1bedbcb98a5fda700b59d5a39bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe0e280fb2ae88434b2f289d056bc9df03138ec16c7bf0ab3c886b9f724d7866(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f596a59670a024842c8b6bf85fb90d757212786265fc745b341cd52e37b36974(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6775b820e2e010ed505c2c056bb183d562860056c0200343b5560c6fd97d3f37(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8c8f84ed420baeeef25229db98d94a86d5691efd65c3a1382fde6135d82f919(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7fde5e7dd448277a23be0c270362275f34dfee9a2e14a7e24e5a606be396e42(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c7c52fb208ccc0ac79a89554245d4cfb25dfbfdac0ddfd0bc104b53851fa519(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39d799fc927b238ffdf322967a8d2fb3e8f45cb86ced165341a387f180786368(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0aa95e592dad1584971b3f5411a0efa40cbb79a50569a626c5e68f8e1701286e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52e3205927ee02d69073c729342f105dced49f239aa4e6d508ca7d66e3750eae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11cdfa6355321d4c6032b728fc521e0c2453ad01c4c3da03559a4d2de5e172e1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__296cde6532523f69511457cdc26337332c9fd8c46e3f5d607a55b2e2e1b50020(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2338310dc30a755fe763c03c2d8674a1f786fd27afc4a739e99a04c2f2fbf326(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4062e03c7672018507387dbc7e2fae902dfd747117b8136282b23026849d962c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7affee528421f8487df3d52f0ce8919a33b8cfba58663674a9a8e37b695d0c4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84a6a4b30af63554027381bf6c01198dc6d31a9d438362851b49f4445380ad1c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    expiration_event_in: typing.Optional[typing.Sequence[builtins.str]] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gen_key: typing.Optional[builtins.str] = None,
    gw_bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    product_type: typing.Optional[typing.Sequence[builtins.str]] = None,
    public_key_data: typing.Optional[builtins.str] = None,
    unique_identifier: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
