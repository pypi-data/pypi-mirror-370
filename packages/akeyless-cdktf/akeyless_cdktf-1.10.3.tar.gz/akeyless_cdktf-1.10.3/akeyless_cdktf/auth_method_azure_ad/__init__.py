'''
# `akeyless_auth_method_azure_ad`

Refer to the Terraform Registry for docs: [`akeyless_auth_method_azure_ad`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad).
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


class AuthMethodAzureAdA(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethodAzureAd.AuthMethodAzureAdA",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad akeyless_auth_method_azure_ad}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        bound_tenant_id: builtins.str,
        name: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_group_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_rg_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_spid: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_sub_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad akeyless_auth_method_azure_ad} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param bound_tenant_id: The Azure tenant id that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_tenant_id AuthMethodAzureAdA#bound_tenant_id}
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#name AuthMethodAzureAdA#name}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#access_expires AuthMethodAzureAdA#access_expires}
        :param audience: The audience in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#audience AuthMethodAzureAdA#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#audit_logs_claims AuthMethodAzureAdA#audit_logs_claims}
        :param bound_group_id: A list of group ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_group_id AuthMethodAzureAdA#bound_group_id}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_ips AuthMethodAzureAdA#bound_ips}
        :param bound_providers: A list of resource providers that the access is restricted to (e.g, Microsoft.Compute, Microsoft.ManagedIdentity, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_providers AuthMethodAzureAdA#bound_providers}
        :param bound_resource_id: A list of full resource ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_id AuthMethodAzureAdA#bound_resource_id}
        :param bound_resource_names: A list of resource names that the access is restricted to (e.g, a virtual machine name, scale set name, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_names AuthMethodAzureAdA#bound_resource_names}
        :param bound_resource_types: A list of resource types that the access is restricted to (e.g, virtualMachines, userAssignedIdentities, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_types AuthMethodAzureAdA#bound_resource_types}
        :param bound_rg_id: A list of resource groups that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_rg_id AuthMethodAzureAdA#bound_rg_id}
        :param bound_spid: A list of service principal IDs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_spid AuthMethodAzureAdA#bound_spid}
        :param bound_sub_id: A list of subscription ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_sub_id AuthMethodAzureAdA#bound_sub_id}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#delete_protection AuthMethodAzureAdA#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#force_sub_claims AuthMethodAzureAdA#force_sub_claims}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#id AuthMethodAzureAdA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#issuer AuthMethodAzureAdA#issuer}
        :param jwks_uri: The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#jwks_uri AuthMethodAzureAdA#jwks_uri}
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#jwt_ttl AuthMethodAzureAdA#jwt_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c77bcdb1383bb9cab283402e5057ddb70f5fc198771e8920d3678d25362b3a18)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodAzureAdAConfig(
            bound_tenant_id=bound_tenant_id,
            name=name,
            access_expires=access_expires,
            audience=audience,
            audit_logs_claims=audit_logs_claims,
            bound_group_id=bound_group_id,
            bound_ips=bound_ips,
            bound_providers=bound_providers,
            bound_resource_id=bound_resource_id,
            bound_resource_names=bound_resource_names,
            bound_resource_types=bound_resource_types,
            bound_rg_id=bound_rg_id,
            bound_spid=bound_spid,
            bound_sub_id=bound_sub_id,
            delete_protection=delete_protection,
            force_sub_claims=force_sub_claims,
            id=id,
            issuer=issuer,
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
        '''Generates CDKTF code for importing a AuthMethodAzureAdA resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethodAzureAdA to import.
        :param import_from_id: The id of the existing AuthMethodAzureAdA that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethodAzureAdA to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edd155c714e4b4428203163246343b36ecc80f897e11d56e87487cb68a2a8ab8)
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

    @jsii.member(jsii_name="resetBoundGroupId")
    def reset_bound_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundGroupId", []))

    @jsii.member(jsii_name="resetBoundIps")
    def reset_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIps", []))

    @jsii.member(jsii_name="resetBoundProviders")
    def reset_bound_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundProviders", []))

    @jsii.member(jsii_name="resetBoundResourceId")
    def reset_bound_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceId", []))

    @jsii.member(jsii_name="resetBoundResourceNames")
    def reset_bound_resource_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceNames", []))

    @jsii.member(jsii_name="resetBoundResourceTypes")
    def reset_bound_resource_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceTypes", []))

    @jsii.member(jsii_name="resetBoundRgId")
    def reset_bound_rg_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundRgId", []))

    @jsii.member(jsii_name="resetBoundSpid")
    def reset_bound_spid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundSpid", []))

    @jsii.member(jsii_name="resetBoundSubId")
    def reset_bound_sub_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundSubId", []))

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
    @jsii.member(jsii_name="boundGroupIdInput")
    def bound_group_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundGroupIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIpsInput")
    def bound_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundProvidersInput")
    def bound_providers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundProvidersInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceIdInput")
    def bound_resource_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceNamesInput")
    def bound_resource_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceTypesInput")
    def bound_resource_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundRgIdInput")
    def bound_rg_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundRgIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundSpidInput")
    def bound_spid_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundSpidInput"))

    @builtins.property
    @jsii.member(jsii_name="boundSubIdInput")
    def bound_sub_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundSubIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundTenantIdInput")
    def bound_tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "boundTenantIdInput"))

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
    @jsii.member(jsii_name="accessExpires")
    def access_expires(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessExpires"))

    @access_expires.setter
    def access_expires(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__616ad4acbff80154856b28c335519fedc059288fb05e6e1e2979fa6f50808722)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e46ecdf304575d07defeb5796644e1962a327ff71f9dbe5ec3df157a31aa320c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value)

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaims")
    def audit_logs_claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditLogsClaims"))

    @audit_logs_claims.setter
    def audit_logs_claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b81e8921d6ef585b3805842b1866e80f83f7962ba1f836a39085dd4b27347cb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditLogsClaims", value)

    @builtins.property
    @jsii.member(jsii_name="boundGroupId")
    def bound_group_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundGroupId"))

    @bound_group_id.setter
    def bound_group_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a0d9c703a587760fa54e21e18e659175dc8592328074e30113510e5176718f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundGroupId", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b04ce448bb3b418f761dedb2303a1103a84f33e41edbaffc21d364e909fc2c40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="boundProviders")
    def bound_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundProviders"))

    @bound_providers.setter
    def bound_providers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__334e561b4faa50ad3d77cd1bf54c2127944a9bdd42af9f9864d61d27847beed9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundProviders", value)

    @builtins.property
    @jsii.member(jsii_name="boundResourceId")
    def bound_resource_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceId"))

    @bound_resource_id.setter
    def bound_resource_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9105022aa0a6dd2fb88655d322a95e063dd51f1c39e2e58a44b81424b3c139cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceId", value)

    @builtins.property
    @jsii.member(jsii_name="boundResourceNames")
    def bound_resource_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceNames"))

    @bound_resource_names.setter
    def bound_resource_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36a492a49de612e2e4eb0c6ce9ffc71107b69b5db43daf6725874f6e8740a2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceNames", value)

    @builtins.property
    @jsii.member(jsii_name="boundResourceTypes")
    def bound_resource_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceTypes"))

    @bound_resource_types.setter
    def bound_resource_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409c05a879a80bb665cc3683a7c4efb8ce5a3e52935e0f957199f905a33b23ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceTypes", value)

    @builtins.property
    @jsii.member(jsii_name="boundRgId")
    def bound_rg_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundRgId"))

    @bound_rg_id.setter
    def bound_rg_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba2ff7be922acb66226285fc9b04163e7944a1f69f04de517384408a4719031b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundRgId", value)

    @builtins.property
    @jsii.member(jsii_name="boundSpid")
    def bound_spid(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundSpid"))

    @bound_spid.setter
    def bound_spid(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36c3e309d1f416e494a000aa41b9aa2e8e3073e0de061b44469a3587df222e9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundSpid", value)

    @builtins.property
    @jsii.member(jsii_name="boundSubId")
    def bound_sub_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundSubId"))

    @bound_sub_id.setter
    def bound_sub_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__084f1d994d690b0cec5728dfbc42ed1ca85b03518031879d3ece7014983054d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundSubId", value)

    @builtins.property
    @jsii.member(jsii_name="boundTenantId")
    def bound_tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "boundTenantId"))

    @bound_tenant_id.setter
    def bound_tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4ee2a2bd92d4668ac787355b222b411efe3201b28a19c3df74f7d4d7f60fed1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundTenantId", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44ff5553eb36bf4b919b308956652253fb42e013bc3e576e68ea4d4c9b4d07d8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__14c2bcea93e2a3cb5d1b22e1a3acb9cec78c063984016fad48f064ad73a94b3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceSubClaims", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96ce13bd8c76b68aeef76279db0f0e71fee2abba1a2d837e7851046d1cbb988f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @issuer.setter
    def issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5a2b5b326bcc4adb1953da44f68a5d146f7e9bade4134287b90af64f617160c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuer", value)

    @builtins.property
    @jsii.member(jsii_name="jwksUri")
    def jwks_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksUri"))

    @jwks_uri.setter
    def jwks_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17f4c62a9f165a4adbcebda8f8b6f6db6b920908770122334528d0c601f0acf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksUri", value)

    @builtins.property
    @jsii.member(jsii_name="jwtTtl")
    def jwt_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jwtTtl"))

    @jwt_ttl.setter
    def jwt_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__617a3887372c5291f829d714eaccec13342d9c858acb9916d0ea60d1bb3ea347)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtTtl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dff12daa97d7061e802ea9bcb03bb7cce679f3e363e73398fa75651aa8ea9fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="akeyless.authMethodAzureAd.AuthMethodAzureAdAConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "bound_tenant_id": "boundTenantId",
        "name": "name",
        "access_expires": "accessExpires",
        "audience": "audience",
        "audit_logs_claims": "auditLogsClaims",
        "bound_group_id": "boundGroupId",
        "bound_ips": "boundIps",
        "bound_providers": "boundProviders",
        "bound_resource_id": "boundResourceId",
        "bound_resource_names": "boundResourceNames",
        "bound_resource_types": "boundResourceTypes",
        "bound_rg_id": "boundRgId",
        "bound_spid": "boundSpid",
        "bound_sub_id": "boundSubId",
        "delete_protection": "deleteProtection",
        "force_sub_claims": "forceSubClaims",
        "id": "id",
        "issuer": "issuer",
        "jwks_uri": "jwksUri",
        "jwt_ttl": "jwtTtl",
    },
)
class AuthMethodAzureAdAConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        bound_tenant_id: builtins.str,
        name: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_group_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_rg_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_spid: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_sub_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        issuer: typing.Optional[builtins.str] = None,
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
        :param bound_tenant_id: The Azure tenant id that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_tenant_id AuthMethodAzureAdA#bound_tenant_id}
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#name AuthMethodAzureAdA#name}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#access_expires AuthMethodAzureAdA#access_expires}
        :param audience: The audience in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#audience AuthMethodAzureAdA#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#audit_logs_claims AuthMethodAzureAdA#audit_logs_claims}
        :param bound_group_id: A list of group ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_group_id AuthMethodAzureAdA#bound_group_id}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_ips AuthMethodAzureAdA#bound_ips}
        :param bound_providers: A list of resource providers that the access is restricted to (e.g, Microsoft.Compute, Microsoft.ManagedIdentity, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_providers AuthMethodAzureAdA#bound_providers}
        :param bound_resource_id: A list of full resource ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_id AuthMethodAzureAdA#bound_resource_id}
        :param bound_resource_names: A list of resource names that the access is restricted to (e.g, a virtual machine name, scale set name, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_names AuthMethodAzureAdA#bound_resource_names}
        :param bound_resource_types: A list of resource types that the access is restricted to (e.g, virtualMachines, userAssignedIdentities, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_types AuthMethodAzureAdA#bound_resource_types}
        :param bound_rg_id: A list of resource groups that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_rg_id AuthMethodAzureAdA#bound_rg_id}
        :param bound_spid: A list of service principal IDs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_spid AuthMethodAzureAdA#bound_spid}
        :param bound_sub_id: A list of subscription ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_sub_id AuthMethodAzureAdA#bound_sub_id}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#delete_protection AuthMethodAzureAdA#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#force_sub_claims AuthMethodAzureAdA#force_sub_claims}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#id AuthMethodAzureAdA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param issuer: Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#issuer AuthMethodAzureAdA#issuer}
        :param jwks_uri: The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#jwks_uri AuthMethodAzureAdA#jwks_uri}
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#jwt_ttl AuthMethodAzureAdA#jwt_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e689f118c3acf0f227b807eecafce15d6743cc92a0be459cc9541e487d831c5)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument bound_tenant_id", value=bound_tenant_id, expected_type=type_hints["bound_tenant_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument access_expires", value=access_expires, expected_type=type_hints["access_expires"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument audit_logs_claims", value=audit_logs_claims, expected_type=type_hints["audit_logs_claims"])
            check_type(argname="argument bound_group_id", value=bound_group_id, expected_type=type_hints["bound_group_id"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument bound_providers", value=bound_providers, expected_type=type_hints["bound_providers"])
            check_type(argname="argument bound_resource_id", value=bound_resource_id, expected_type=type_hints["bound_resource_id"])
            check_type(argname="argument bound_resource_names", value=bound_resource_names, expected_type=type_hints["bound_resource_names"])
            check_type(argname="argument bound_resource_types", value=bound_resource_types, expected_type=type_hints["bound_resource_types"])
            check_type(argname="argument bound_rg_id", value=bound_rg_id, expected_type=type_hints["bound_rg_id"])
            check_type(argname="argument bound_spid", value=bound_spid, expected_type=type_hints["bound_spid"])
            check_type(argname="argument bound_sub_id", value=bound_sub_id, expected_type=type_hints["bound_sub_id"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument force_sub_claims", value=force_sub_claims, expected_type=type_hints["force_sub_claims"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument issuer", value=issuer, expected_type=type_hints["issuer"])
            check_type(argname="argument jwks_uri", value=jwks_uri, expected_type=type_hints["jwks_uri"])
            check_type(argname="argument jwt_ttl", value=jwt_ttl, expected_type=type_hints["jwt_ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bound_tenant_id": bound_tenant_id,
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
        if audience is not None:
            self._values["audience"] = audience
        if audit_logs_claims is not None:
            self._values["audit_logs_claims"] = audit_logs_claims
        if bound_group_id is not None:
            self._values["bound_group_id"] = bound_group_id
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if bound_providers is not None:
            self._values["bound_providers"] = bound_providers
        if bound_resource_id is not None:
            self._values["bound_resource_id"] = bound_resource_id
        if bound_resource_names is not None:
            self._values["bound_resource_names"] = bound_resource_names
        if bound_resource_types is not None:
            self._values["bound_resource_types"] = bound_resource_types
        if bound_rg_id is not None:
            self._values["bound_rg_id"] = bound_rg_id
        if bound_spid is not None:
            self._values["bound_spid"] = bound_spid
        if bound_sub_id is not None:
            self._values["bound_sub_id"] = bound_sub_id
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if force_sub_claims is not None:
            self._values["force_sub_claims"] = force_sub_claims
        if id is not None:
            self._values["id"] = id
        if issuer is not None:
            self._values["issuer"] = issuer
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
    def bound_tenant_id(self) -> builtins.str:
        '''The Azure tenant id that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_tenant_id AuthMethodAzureAdA#bound_tenant_id}
        '''
        result = self._values.get("bound_tenant_id")
        assert result is not None, "Required property 'bound_tenant_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Auth Method name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#name AuthMethodAzureAdA#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#access_expires AuthMethodAzureAdA#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''The audience in the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#audience AuthMethodAzureAdA#audience}
        '''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def audit_logs_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Subclaims to include in audit logs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#audit_logs_claims AuthMethodAzureAdA#audit_logs_claims}
        '''
        result = self._values.get("audit_logs_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_group_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of group ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_group_id AuthMethodAzureAdA#bound_group_id}
        '''
        result = self._values.get("bound_group_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A CIDR whitelist with the IPs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_ips AuthMethodAzureAdA#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_providers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource providers that the access is restricted to (e.g, Microsoft.Compute, Microsoft.ManagedIdentity, etc).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_providers AuthMethodAzureAdA#bound_providers}
        '''
        result = self._values.get("bound_providers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full resource ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_id AuthMethodAzureAdA#bound_resource_id}
        '''
        result = self._values.get("bound_resource_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource names that the access is restricted to (e.g, a virtual machine name, scale set name, etc).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_names AuthMethodAzureAdA#bound_resource_names}
        '''
        result = self._values.get("bound_resource_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource types that the access is restricted to (e.g, virtualMachines, userAssignedIdentities, etc).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_resource_types AuthMethodAzureAdA#bound_resource_types}
        '''
        result = self._values.get("bound_resource_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_rg_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource groups that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_rg_id AuthMethodAzureAdA#bound_rg_id}
        '''
        result = self._values.get("bound_rg_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_spid(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of service principal IDs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_spid AuthMethodAzureAdA#bound_spid}
        '''
        result = self._values.get("bound_spid")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_sub_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of subscription ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#bound_sub_id AuthMethodAzureAdA#bound_sub_id}
        '''
        result = self._values.get("bound_sub_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this auth method, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#delete_protection AuthMethodAzureAdA#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_sub_claims(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''enforce role-association must include sub claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#force_sub_claims AuthMethodAzureAdA#force_sub_claims}
        '''
        result = self._values.get("force_sub_claims")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#id AuthMethodAzureAdA#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def issuer(self) -> typing.Optional[builtins.str]:
        '''Issuer URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#issuer AuthMethodAzureAdA#issuer}
        '''
        result = self._values.get("issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_uri(self) -> typing.Optional[builtins.str]:
        '''The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#jwks_uri AuthMethodAzureAdA#jwks_uri}
        '''
        result = self._values.get("jwks_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_ttl(self) -> typing.Optional[jsii.Number]:
        '''Creds expiration time in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_azure_ad#jwt_ttl AuthMethodAzureAdA#jwt_ttl}
        '''
        result = self._values.get("jwt_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodAzureAdAConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthMethodAzureAdA",
    "AuthMethodAzureAdAConfig",
]

publication.publish()

def _typecheckingstub__c77bcdb1383bb9cab283402e5057ddb70f5fc198771e8920d3678d25362b3a18(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    bound_tenant_id: builtins.str,
    name: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_group_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_rg_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_spid: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_sub_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__edd155c714e4b4428203163246343b36ecc80f897e11d56e87487cb68a2a8ab8(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__616ad4acbff80154856b28c335519fedc059288fb05e6e1e2979fa6f50808722(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e46ecdf304575d07defeb5796644e1962a327ff71f9dbe5ec3df157a31aa320c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b81e8921d6ef585b3805842b1866e80f83f7962ba1f836a39085dd4b27347cb1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a0d9c703a587760fa54e21e18e659175dc8592328074e30113510e5176718f1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b04ce448bb3b418f761dedb2303a1103a84f33e41edbaffc21d364e909fc2c40(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__334e561b4faa50ad3d77cd1bf54c2127944a9bdd42af9f9864d61d27847beed9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9105022aa0a6dd2fb88655d322a95e063dd51f1c39e2e58a44b81424b3c139cd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36a492a49de612e2e4eb0c6ce9ffc71107b69b5db43daf6725874f6e8740a2a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409c05a879a80bb665cc3683a7c4efb8ce5a3e52935e0f957199f905a33b23ea(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba2ff7be922acb66226285fc9b04163e7944a1f69f04de517384408a4719031b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36c3e309d1f416e494a000aa41b9aa2e8e3073e0de061b44469a3587df222e9a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__084f1d994d690b0cec5728dfbc42ed1ca85b03518031879d3ece7014983054d6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4ee2a2bd92d4668ac787355b222b411efe3201b28a19c3df74f7d4d7f60fed1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44ff5553eb36bf4b919b308956652253fb42e013bc3e576e68ea4d4c9b4d07d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14c2bcea93e2a3cb5d1b22e1a3acb9cec78c063984016fad48f064ad73a94b3f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96ce13bd8c76b68aeef76279db0f0e71fee2abba1a2d837e7851046d1cbb988f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5a2b5b326bcc4adb1953da44f68a5d146f7e9bade4134287b90af64f617160c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17f4c62a9f165a4adbcebda8f8b6f6db6b920908770122334528d0c601f0acf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__617a3887372c5291f829d714eaccec13342d9c858acb9916d0ea60d1bb3ea347(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dff12daa97d7061e802ea9bcb03bb7cce679f3e363e73398fa75651aa8ea9fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e689f118c3acf0f227b807eecafce15d6743cc92a0be459cc9541e487d831c5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    bound_tenant_id: builtins.str,
    name: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_group_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_rg_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_spid: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_sub_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    issuer: typing.Optional[builtins.str] = None,
    jwks_uri: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
