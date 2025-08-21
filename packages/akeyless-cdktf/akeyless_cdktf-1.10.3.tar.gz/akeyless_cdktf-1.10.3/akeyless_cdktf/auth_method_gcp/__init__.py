'''
# `akeyless_auth_method_gcp`

Refer to the Terraform Registry for docs: [`akeyless_auth_method_gcp`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp).
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


class AuthMethodGcpA(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethodGcp.AuthMethodGcpA",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp akeyless_auth_method_gcp}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        type: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_projects: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        service_account_creds_data: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp akeyless_auth_method_gcp} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#name AuthMethodGcpA#name}
        :param type: The type of the GCP Auth Method (iam/gce). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#type AuthMethodGcpA#type}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#access_expires AuthMethodGcpA#access_expires}
        :param audience: The audience to verify in the JWT received by the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#audience AuthMethodGcpA#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#audit_logs_claims AuthMethodGcpA#audit_logs_claims}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_ips AuthMethodGcpA#bound_ips}
        :param bound_labels: GCE only. A list of GCP labels formatted as key:value pairs that must be set on instances in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_labels AuthMethodGcpA#bound_labels}
        :param bound_projects: A list of GCP project IDs. Clients must belong to any of the provided projects in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_projects AuthMethodGcpA#bound_projects}
        :param bound_regions: GCE only. A list of regions. GCE instances must belong to any of the provided regions in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_regions AuthMethodGcpA#bound_regions}
        :param bound_service_accounts: A list of Service Accounts. Clients must belong to any of the provided service accounts in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_service_accounts AuthMethodGcpA#bound_service_accounts}
        :param bound_zones: GCE only. A list of zones. GCE instances must belong to any of the provided zones in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_zones AuthMethodGcpA#bound_zones}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#delete_protection AuthMethodGcpA#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#force_sub_claims AuthMethodGcpA#force_sub_claims}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#id AuthMethodGcpA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#jwt_ttl AuthMethodGcpA#jwt_ttl}
        :param service_account_creds_data: Service Account creds data, base64 encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#service_account_creds_data AuthMethodGcpA#service_account_creds_data}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c8194b9bd78005f6a24f3c91ff5907bd6f2fb59c843a3db0cd24e9cbb7d8e0e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodGcpAConfig(
            name=name,
            type=type,
            access_expires=access_expires,
            audience=audience,
            audit_logs_claims=audit_logs_claims,
            bound_ips=bound_ips,
            bound_labels=bound_labels,
            bound_projects=bound_projects,
            bound_regions=bound_regions,
            bound_service_accounts=bound_service_accounts,
            bound_zones=bound_zones,
            delete_protection=delete_protection,
            force_sub_claims=force_sub_claims,
            id=id,
            jwt_ttl=jwt_ttl,
            service_account_creds_data=service_account_creds_data,
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
        '''Generates CDKTF code for importing a AuthMethodGcpA resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethodGcpA to import.
        :param import_from_id: The id of the existing AuthMethodGcpA that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethodGcpA to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ecb1d3de621d9781efc9a78064d2535532f2790d11167e62f83a4849268e5fd)
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

    @jsii.member(jsii_name="resetBoundIps")
    def reset_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIps", []))

    @jsii.member(jsii_name="resetBoundLabels")
    def reset_bound_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundLabels", []))

    @jsii.member(jsii_name="resetBoundProjects")
    def reset_bound_projects(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundProjects", []))

    @jsii.member(jsii_name="resetBoundRegions")
    def reset_bound_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundRegions", []))

    @jsii.member(jsii_name="resetBoundServiceAccounts")
    def reset_bound_service_accounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundServiceAccounts", []))

    @jsii.member(jsii_name="resetBoundZones")
    def reset_bound_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundZones", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetForceSubClaims")
    def reset_force_sub_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceSubClaims", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJwtTtl")
    def reset_jwt_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtTtl", []))

    @jsii.member(jsii_name="resetServiceAccountCredsData")
    def reset_service_account_creds_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountCredsData", []))

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
    @jsii.member(jsii_name="boundIpsInput")
    def bound_ips_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundLabelsInput")
    def bound_labels_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundLabelsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundProjectsInput")
    def bound_projects_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundProjectsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundRegionsInput")
    def bound_regions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundRegionsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundServiceAccountsInput")
    def bound_service_accounts_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundServiceAccountsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundZonesInput")
    def bound_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundZonesInput"))

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
    @jsii.member(jsii_name="jwtTtlInput")
    def jwt_ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "jwtTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountCredsDataInput")
    def service_account_creds_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountCredsDataInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="accessExpires")
    def access_expires(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessExpires"))

    @access_expires.setter
    def access_expires(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2263140a0954fb52832d3647050da9ea8dada34af5770e8d95993ca072dcdf5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__325c1a8f3a6691ba55c7ce5680d7e5862f0a64166b016eba34c0bc5b1d785f69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value)

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaims")
    def audit_logs_claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditLogsClaims"))

    @audit_logs_claims.setter
    def audit_logs_claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__234ef8073e7326b3cfdb12b07c46c9de755d4ba6eca55c270b9605f3e0a6b33e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditLogsClaims", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77f7c9a1f1aadd44d8706fa1cdf0d51ce77243a0e07de9a55a3aeaed242cf5c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="boundLabels")
    def bound_labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundLabels"))

    @bound_labels.setter
    def bound_labels(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1e09d8a3e0c18598d2f3aaffee1e3a1b5ae9de411ec0ce757ee43c186d66b67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundLabels", value)

    @builtins.property
    @jsii.member(jsii_name="boundProjects")
    def bound_projects(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundProjects"))

    @bound_projects.setter
    def bound_projects(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a01869814cede3b48d0e93ededd00970b5716b0f9a13889c38f44e969c8c3ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundProjects", value)

    @builtins.property
    @jsii.member(jsii_name="boundRegions")
    def bound_regions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundRegions"))

    @bound_regions.setter
    def bound_regions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3a63e60d0ff9c76d73368ce2ed7ff4bd88447bf453e5ea71b71d9601183c361)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundRegions", value)

    @builtins.property
    @jsii.member(jsii_name="boundServiceAccounts")
    def bound_service_accounts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundServiceAccounts"))

    @bound_service_accounts.setter
    def bound_service_accounts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b3505f4548df38c5b902a1bc2d37e220311e028e397fdf2674d5057a49c7ad1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundServiceAccounts", value)

    @builtins.property
    @jsii.member(jsii_name="boundZones")
    def bound_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundZones"))

    @bound_zones.setter
    def bound_zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b6ab3d346de4d593e5e5741339869f77a01d12132cf9be6ba591b83ca0d11c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundZones", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__619b9ca93d91a14cfa3cf76264b438bf81309fd68ed13456a361aba0f069dd62)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d3721fbfb0cf2c0347fc87462eb239f74f374a0d191bc799ac6e8d975fd6d53b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceSubClaims", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9381e3aa796691c34a15e681d5cf8557cd0951b4e11e0a945064b09e9123bad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="jwtTtl")
    def jwt_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jwtTtl"))

    @jwt_ttl.setter
    def jwt_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58a617287f284efcd925ef31013707b17afcfd40fc36517350d30e3d32cf23cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtTtl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7b81e3e57d6a44ee5ca6121de8a8766597afdae51233d1240853c8252f7cc83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="serviceAccountCredsData")
    def service_account_creds_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountCredsData"))

    @service_account_creds_data.setter
    def service_account_creds_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c303b1cd47e2b9ff62a58908348c61b6ec35c033841d0168b83dea936ff77403)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountCredsData", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54a2963f5c82cf5fae47e7789d3db04812f449951073a3c6d36fde3ccc32a35f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="akeyless.authMethodGcp.AuthMethodGcpAConfig",
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
        "type": "type",
        "access_expires": "accessExpires",
        "audience": "audience",
        "audit_logs_claims": "auditLogsClaims",
        "bound_ips": "boundIps",
        "bound_labels": "boundLabels",
        "bound_projects": "boundProjects",
        "bound_regions": "boundRegions",
        "bound_service_accounts": "boundServiceAccounts",
        "bound_zones": "boundZones",
        "delete_protection": "deleteProtection",
        "force_sub_claims": "forceSubClaims",
        "id": "id",
        "jwt_ttl": "jwtTtl",
        "service_account_creds_data": "serviceAccountCredsData",
    },
)
class AuthMethodGcpAConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        type: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_projects: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        service_account_creds_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#name AuthMethodGcpA#name}
        :param type: The type of the GCP Auth Method (iam/gce). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#type AuthMethodGcpA#type}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#access_expires AuthMethodGcpA#access_expires}
        :param audience: The audience to verify in the JWT received by the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#audience AuthMethodGcpA#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#audit_logs_claims AuthMethodGcpA#audit_logs_claims}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_ips AuthMethodGcpA#bound_ips}
        :param bound_labels: GCE only. A list of GCP labels formatted as key:value pairs that must be set on instances in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_labels AuthMethodGcpA#bound_labels}
        :param bound_projects: A list of GCP project IDs. Clients must belong to any of the provided projects in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_projects AuthMethodGcpA#bound_projects}
        :param bound_regions: GCE only. A list of regions. GCE instances must belong to any of the provided regions in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_regions AuthMethodGcpA#bound_regions}
        :param bound_service_accounts: A list of Service Accounts. Clients must belong to any of the provided service accounts in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_service_accounts AuthMethodGcpA#bound_service_accounts}
        :param bound_zones: GCE only. A list of zones. GCE instances must belong to any of the provided zones in order to authenticate. For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_zones AuthMethodGcpA#bound_zones}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#delete_protection AuthMethodGcpA#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#force_sub_claims AuthMethodGcpA#force_sub_claims}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#id AuthMethodGcpA#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#jwt_ttl AuthMethodGcpA#jwt_ttl}
        :param service_account_creds_data: Service Account creds data, base64 encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#service_account_creds_data AuthMethodGcpA#service_account_creds_data}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc880330eaa84483a6779da6311f5e09e92754e15b6127687c0071fc19958d48)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument access_expires", value=access_expires, expected_type=type_hints["access_expires"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument audit_logs_claims", value=audit_logs_claims, expected_type=type_hints["audit_logs_claims"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument bound_labels", value=bound_labels, expected_type=type_hints["bound_labels"])
            check_type(argname="argument bound_projects", value=bound_projects, expected_type=type_hints["bound_projects"])
            check_type(argname="argument bound_regions", value=bound_regions, expected_type=type_hints["bound_regions"])
            check_type(argname="argument bound_service_accounts", value=bound_service_accounts, expected_type=type_hints["bound_service_accounts"])
            check_type(argname="argument bound_zones", value=bound_zones, expected_type=type_hints["bound_zones"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument force_sub_claims", value=force_sub_claims, expected_type=type_hints["force_sub_claims"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jwt_ttl", value=jwt_ttl, expected_type=type_hints["jwt_ttl"])
            check_type(argname="argument service_account_creds_data", value=service_account_creds_data, expected_type=type_hints["service_account_creds_data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "type": type,
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
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if bound_labels is not None:
            self._values["bound_labels"] = bound_labels
        if bound_projects is not None:
            self._values["bound_projects"] = bound_projects
        if bound_regions is not None:
            self._values["bound_regions"] = bound_regions
        if bound_service_accounts is not None:
            self._values["bound_service_accounts"] = bound_service_accounts
        if bound_zones is not None:
            self._values["bound_zones"] = bound_zones
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if force_sub_claims is not None:
            self._values["force_sub_claims"] = force_sub_claims
        if id is not None:
            self._values["id"] = id
        if jwt_ttl is not None:
            self._values["jwt_ttl"] = jwt_ttl
        if service_account_creds_data is not None:
            self._values["service_account_creds_data"] = service_account_creds_data

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#name AuthMethodGcpA#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The type of the GCP Auth Method (iam/gce).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#type AuthMethodGcpA#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#access_expires AuthMethodGcpA#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''The audience to verify in the JWT received by the client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#audience AuthMethodGcpA#audience}
        '''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def audit_logs_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Subclaims to include in audit logs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#audit_logs_claims AuthMethodGcpA#audit_logs_claims}
        '''
        result = self._values.get("audit_logs_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A CIDR whitelist with the IPs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_ips AuthMethodGcpA#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''GCE only.

        A list of GCP labels formatted as key:value pairs that must be set on instances in order to authenticate. For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_labels AuthMethodGcpA#bound_labels}
        '''
        result = self._values.get("bound_labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_projects(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of GCP project IDs.

        Clients must belong to any of the provided projects in order to authenticate. For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_projects AuthMethodGcpA#bound_projects}
        '''
        result = self._values.get("bound_projects")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''GCE only.

        A list of regions. GCE instances must belong to any of the provided regions in order to authenticate. For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_regions AuthMethodGcpA#bound_regions}
        '''
        result = self._values.get("bound_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_service_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of Service Accounts.

        Clients must belong to any of the provided service accounts in order to authenticate. For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_service_accounts AuthMethodGcpA#bound_service_accounts}
        '''
        result = self._values.get("bound_service_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''GCE only.

        A list of zones. GCE instances must belong to any of the provided zones in order to authenticate. For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#bound_zones AuthMethodGcpA#bound_zones}
        '''
        result = self._values.get("bound_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this auth method, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#delete_protection AuthMethodGcpA#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_sub_claims(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''enforce role-association must include sub claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#force_sub_claims AuthMethodGcpA#force_sub_claims}
        '''
        result = self._values.get("force_sub_claims")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#id AuthMethodGcpA#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_ttl(self) -> typing.Optional[jsii.Number]:
        '''Creds expiration time in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#jwt_ttl AuthMethodGcpA#jwt_ttl}
        '''
        result = self._values.get("jwt_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def service_account_creds_data(self) -> typing.Optional[builtins.str]:
        '''Service Account creds data, base64 encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_gcp#service_account_creds_data AuthMethodGcpA#service_account_creds_data}
        '''
        result = self._values.get("service_account_creds_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodGcpAConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthMethodGcpA",
    "AuthMethodGcpAConfig",
]

publication.publish()

def _typecheckingstub__4c8194b9bd78005f6a24f3c91ff5907bd6f2fb59c843a3db0cd24e9cbb7d8e0e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    type: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_projects: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    service_account_creds_data: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__0ecb1d3de621d9781efc9a78064d2535532f2790d11167e62f83a4849268e5fd(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2263140a0954fb52832d3647050da9ea8dada34af5770e8d95993ca072dcdf5b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__325c1a8f3a6691ba55c7ce5680d7e5862f0a64166b016eba34c0bc5b1d785f69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__234ef8073e7326b3cfdb12b07c46c9de755d4ba6eca55c270b9605f3e0a6b33e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77f7c9a1f1aadd44d8706fa1cdf0d51ce77243a0e07de9a55a3aeaed242cf5c3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1e09d8a3e0c18598d2f3aaffee1e3a1b5ae9de411ec0ce757ee43c186d66b67(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a01869814cede3b48d0e93ededd00970b5716b0f9a13889c38f44e969c8c3ef(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3a63e60d0ff9c76d73368ce2ed7ff4bd88447bf453e5ea71b71d9601183c361(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b3505f4548df38c5b902a1bc2d37e220311e028e397fdf2674d5057a49c7ad1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b6ab3d346de4d593e5e5741339869f77a01d12132cf9be6ba591b83ca0d11c2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__619b9ca93d91a14cfa3cf76264b438bf81309fd68ed13456a361aba0f069dd62(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3721fbfb0cf2c0347fc87462eb239f74f374a0d191bc799ac6e8d975fd6d53b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9381e3aa796691c34a15e681d5cf8557cd0951b4e11e0a945064b09e9123bad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58a617287f284efcd925ef31013707b17afcfd40fc36517350d30e3d32cf23cb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7b81e3e57d6a44ee5ca6121de8a8766597afdae51233d1240853c8252f7cc83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c303b1cd47e2b9ff62a58908348c61b6ec35c033841d0168b83dea936ff77403(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54a2963f5c82cf5fae47e7789d3db04812f449951073a3c6d36fde3ccc32a35f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc880330eaa84483a6779da6311f5e09e92754e15b6127687c0071fc19958d48(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    type: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_projects: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    service_account_creds_data: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
