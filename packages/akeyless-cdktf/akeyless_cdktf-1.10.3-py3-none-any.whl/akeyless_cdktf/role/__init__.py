'''
# `akeyless_role`

Refer to the Terraform Registry for docs: [`akeyless_role`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role).
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


class Role(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.role.Role",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role akeyless_role}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        analytics_access: typing.Optional[builtins.str] = None,
        assoc_auth_method: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RoleAssocAuthMethod", typing.Dict[builtins.str, typing.Any]]]]] = None,
        audit_access: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        event_center_access: typing.Optional[builtins.str] = None,
        event_forwarders_access: typing.Optional[builtins.str] = None,
        gw_analytics_access: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RoleRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        sra_reports_access: typing.Optional[builtins.str] = None,
        usage_reports_access: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role akeyless_role} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Role name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#name Role#name}
        :param analytics_access: Allow this role to view analytics. Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view reports produced by the same auth methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#analytics_access Role#analytics_access}
        :param assoc_auth_method: assoc_auth_method block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#assoc_auth_method Role#assoc_auth_method}
        :param audit_access: Allow this role to view audit logs. Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view audit logs produced by the same auth methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#audit_access Role#audit_access}
        :param delete_protection: Protection from accidental deletion of this role, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#delete_protection Role#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#description Role#description}
        :param event_center_access: Allow this role to view Event Center. Currently only 'none', 'own' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#event_center_access Role#event_center_access}
        :param event_forwarders_access: Allow this role to manage Event Forwarders. Currently only 'none' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#event_forwarders_access Role#event_forwarders_access}
        :param gw_analytics_access: Allow this role to view gw analytics. Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view reports produced by the same auth methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#gw_analytics_access Role#gw_analytics_access}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#id Role#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rules: rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#rules Role#rules}
        :param sra_reports_access: Allow this role to view SRA Clusters. Currently only 'none', 'own' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#sra_reports_access Role#sra_reports_access}
        :param usage_reports_access: Allow this role to view Usage reports. Currently only 'none' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#usage_reports_access Role#usage_reports_access}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad2fe649f53d40ca27c79c898c88c564c0f83369f7b100f2695e81cad85c97fb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RoleConfig(
            name=name,
            analytics_access=analytics_access,
            assoc_auth_method=assoc_auth_method,
            audit_access=audit_access,
            delete_protection=delete_protection,
            description=description,
            event_center_access=event_center_access,
            event_forwarders_access=event_forwarders_access,
            gw_analytics_access=gw_analytics_access,
            id=id,
            rules=rules,
            sra_reports_access=sra_reports_access,
            usage_reports_access=usage_reports_access,
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
        '''Generates CDKTF code for importing a Role resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Role to import.
        :param import_from_id: The id of the existing Role that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Role to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4bd5e378a7d5a7c2d5b221d8871c30f71c4f8abb4eeb92f75b40110a0f04904)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAssocAuthMethod")
    def put_assoc_auth_method(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RoleAssocAuthMethod", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7695cfb5994ac5f055ce8091f09dfa8eb76bff3504a3f8ba2b9dfae1099497a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAssocAuthMethod", [value]))

    @jsii.member(jsii_name="putRules")
    def put_rules(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RoleRules", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ba235436d6c6c1956bd3c4c502d36e1b28b7b6e0709e63487ed417f0c23b03d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRules", [value]))

    @jsii.member(jsii_name="resetAnalyticsAccess")
    def reset_analytics_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnalyticsAccess", []))

    @jsii.member(jsii_name="resetAssocAuthMethod")
    def reset_assoc_auth_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssocAuthMethod", []))

    @jsii.member(jsii_name="resetAuditAccess")
    def reset_audit_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuditAccess", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEventCenterAccess")
    def reset_event_center_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventCenterAccess", []))

    @jsii.member(jsii_name="resetEventForwardersAccess")
    def reset_event_forwarders_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventForwardersAccess", []))

    @jsii.member(jsii_name="resetGwAnalyticsAccess")
    def reset_gw_analytics_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGwAnalyticsAccess", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRules")
    def reset_rules(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRules", []))

    @jsii.member(jsii_name="resetSraReportsAccess")
    def reset_sra_reports_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSraReportsAccess", []))

    @jsii.member(jsii_name="resetUsageReportsAccess")
    def reset_usage_reports_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsageReportsAccess", []))

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
    @jsii.member(jsii_name="assocAuthMethod")
    def assoc_auth_method(self) -> "RoleAssocAuthMethodList":
        return typing.cast("RoleAssocAuthMethodList", jsii.get(self, "assocAuthMethod"))

    @builtins.property
    @jsii.member(jsii_name="restrictedRules")
    def restricted_rules(self) -> "RoleRestrictedRulesList":
        return typing.cast("RoleRestrictedRulesList", jsii.get(self, "restrictedRules"))

    @builtins.property
    @jsii.member(jsii_name="rules")
    def rules(self) -> "RoleRulesList":
        return typing.cast("RoleRulesList", jsii.get(self, "rules"))

    @builtins.property
    @jsii.member(jsii_name="analyticsAccessInput")
    def analytics_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "analyticsAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="assocAuthMethodInput")
    def assoc_auth_method_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RoleAssocAuthMethod"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RoleAssocAuthMethod"]]], jsii.get(self, "assocAuthMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="auditAccessInput")
    def audit_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "auditAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="eventCenterAccessInput")
    def event_center_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventCenterAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="eventForwardersAccessInput")
    def event_forwarders_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventForwardersAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="gwAnalyticsAccessInput")
    def gw_analytics_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gwAnalyticsAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="rulesInput")
    def rules_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RoleRules"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RoleRules"]]], jsii.get(self, "rulesInput"))

    @builtins.property
    @jsii.member(jsii_name="sraReportsAccessInput")
    def sra_reports_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sraReportsAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="usageReportsAccessInput")
    def usage_reports_access_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usageReportsAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="analyticsAccess")
    def analytics_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "analyticsAccess"))

    @analytics_access.setter
    def analytics_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa06cf4733203ea0ab8c596275ecb2b90aae02286b0bb5d5975c7e5a467c577e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "analyticsAccess", value)

    @builtins.property
    @jsii.member(jsii_name="auditAccess")
    def audit_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "auditAccess"))

    @audit_access.setter
    def audit_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71404befd0b09288f3c76f88fe7b52ce4965f8caa816568518cd21c460567683)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditAccess", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8909d6d9517e42a56089a72ffaea2e704846c06c592b7b75c1b11526ebf043f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11fcdd1956faf122780297b1247b6b9db9e6f4b0ca020db8533725055e1d1414)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="eventCenterAccess")
    def event_center_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventCenterAccess"))

    @event_center_access.setter
    def event_center_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccca3ebc764304f8d51acbec80ba515e68aeae3eaf2812de0f1196d93214ca50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventCenterAccess", value)

    @builtins.property
    @jsii.member(jsii_name="eventForwardersAccess")
    def event_forwarders_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventForwardersAccess"))

    @event_forwarders_access.setter
    def event_forwarders_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f016e4bf9bcff6195121b75cfa883ee1949e1580dfde57b124f9c3383170b741)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventForwardersAccess", value)

    @builtins.property
    @jsii.member(jsii_name="gwAnalyticsAccess")
    def gw_analytics_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gwAnalyticsAccess"))

    @gw_analytics_access.setter
    def gw_analytics_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8731e95cf8b83b2598eeeb630a5ad50ddd4c0a34316482b98ca05a3bb3bed0d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gwAnalyticsAccess", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81408afbf44be3bd59f3377acad0a456867606340f5d914e55a50b0149abb312)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32b80fec2414bb2e7fc5316ba8851bb35542235570d347ffcdbca921bf8c7c58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="sraReportsAccess")
    def sra_reports_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sraReportsAccess"))

    @sra_reports_access.setter
    def sra_reports_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2596b75805e9dd78db5c90fa9c1f5377497ada7951179b6e11fb0b6c38f44b61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sraReportsAccess", value)

    @builtins.property
    @jsii.member(jsii_name="usageReportsAccess")
    def usage_reports_access(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usageReportsAccess"))

    @usage_reports_access.setter
    def usage_reports_access(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b246e9f0b6835b4efcb2b404bf3ff54dbc38f47482f82931a2e0deb59bbd02b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usageReportsAccess", value)


@jsii.data_type(
    jsii_type="akeyless.role.RoleAssocAuthMethod",
    jsii_struct_bases=[],
    name_mapping={
        "am_name": "amName",
        "case_sensitive": "caseSensitive",
        "sub_claims": "subClaims",
    },
)
class RoleAssocAuthMethod:
    def __init__(
        self,
        *,
        am_name: builtins.str,
        case_sensitive: typing.Optional[builtins.str] = None,
        sub_claims: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param am_name: The auth method to associate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#am_name Role#am_name}
        :param case_sensitive: Treat sub claims as case-sensitive. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#case_sensitive Role#case_sensitive}
        :param sub_claims: key/val of sub claims, e.g group=admins,developers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#sub_claims Role#sub_claims}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbd5f8f2e3958da7c7749cff8e25e1ef5ce1269a3cdf6f7b83d1ad53ddd253cb)
            check_type(argname="argument am_name", value=am_name, expected_type=type_hints["am_name"])
            check_type(argname="argument case_sensitive", value=case_sensitive, expected_type=type_hints["case_sensitive"])
            check_type(argname="argument sub_claims", value=sub_claims, expected_type=type_hints["sub_claims"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "am_name": am_name,
        }
        if case_sensitive is not None:
            self._values["case_sensitive"] = case_sensitive
        if sub_claims is not None:
            self._values["sub_claims"] = sub_claims

    @builtins.property
    def am_name(self) -> builtins.str:
        '''The auth method to associate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#am_name Role#am_name}
        '''
        result = self._values.get("am_name")
        assert result is not None, "Required property 'am_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def case_sensitive(self) -> typing.Optional[builtins.str]:
        '''Treat sub claims as case-sensitive.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#case_sensitive Role#case_sensitive}
        '''
        result = self._values.get("case_sensitive")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sub_claims(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''key/val of sub claims, e.g group=admins,developers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#sub_claims Role#sub_claims}
        '''
        result = self._values.get("sub_claims")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleAssocAuthMethod(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RoleAssocAuthMethodList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.role.RoleAssocAuthMethodList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c43b6ff0e34e73976db336b88d1aebd5f968accf06e8ffc4706e4df946e7c571)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "RoleAssocAuthMethodOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5aff2f008971595e3c3003df7bffc71334af68faf395c29680969ff74bbf139b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RoleAssocAuthMethodOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93638dca2672194822b511681a0ae627b96afe8e4eeff8435843cdd6ebbed72f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__166f9247f31d39425ef6e44d84da8cbab12f70124cb4306ff04aecd789fddefa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59c3761885fed4862b565b80b802752d980a8292669f5ef7f0b68e8c603a83f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleAssocAuthMethod]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleAssocAuthMethod]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleAssocAuthMethod]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6cbb395a05f212f42d779119538a81593bd9b3eb1d384d350727ede66f4af40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class RoleAssocAuthMethodOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.role.RoleAssocAuthMethodOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a68595affb424b47134b643770af3e34227517f89a19e3131da09be726b01e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCaseSensitive")
    def reset_case_sensitive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaseSensitive", []))

    @jsii.member(jsii_name="resetSubClaims")
    def reset_sub_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubClaims", []))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @builtins.property
    @jsii.member(jsii_name="assocId")
    def assoc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "assocId"))

    @builtins.property
    @jsii.member(jsii_name="amNameInput")
    def am_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "amNameInput"))

    @builtins.property
    @jsii.member(jsii_name="caseSensitiveInput")
    def case_sensitive_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caseSensitiveInput"))

    @builtins.property
    @jsii.member(jsii_name="subClaimsInput")
    def sub_claims_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "subClaimsInput"))

    @builtins.property
    @jsii.member(jsii_name="amName")
    def am_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "amName"))

    @am_name.setter
    def am_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f40aff4da235114770412e41a76ac3e432c988ba6bc262566ae8123273397640)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amName", value)

    @builtins.property
    @jsii.member(jsii_name="caseSensitive")
    def case_sensitive(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caseSensitive"))

    @case_sensitive.setter
    def case_sensitive(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8570511a68afcc50b24fcc1bd6ca243cddddc37adda71420df514b4bf7ed9869)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caseSensitive", value)

    @builtins.property
    @jsii.member(jsii_name="subClaims")
    def sub_claims(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "subClaims"))

    @sub_claims.setter
    def sub_claims(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd47669bc36f35c1264f055774a0ccaac72ab56057d092b35747acb970fc3903)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subClaims", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleAssocAuthMethod]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleAssocAuthMethod]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleAssocAuthMethod]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd3a1ed58d360c7bb16048f50543608bda5fc9cd11768a172969acdb905358e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.role.RoleConfig",
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
        "analytics_access": "analyticsAccess",
        "assoc_auth_method": "assocAuthMethod",
        "audit_access": "auditAccess",
        "delete_protection": "deleteProtection",
        "description": "description",
        "event_center_access": "eventCenterAccess",
        "event_forwarders_access": "eventForwardersAccess",
        "gw_analytics_access": "gwAnalyticsAccess",
        "id": "id",
        "rules": "rules",
        "sra_reports_access": "sraReportsAccess",
        "usage_reports_access": "usageReportsAccess",
    },
)
class RoleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        analytics_access: typing.Optional[builtins.str] = None,
        assoc_auth_method: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RoleAssocAuthMethod, typing.Dict[builtins.str, typing.Any]]]]] = None,
        audit_access: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        event_center_access: typing.Optional[builtins.str] = None,
        event_forwarders_access: typing.Optional[builtins.str] = None,
        gw_analytics_access: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RoleRules", typing.Dict[builtins.str, typing.Any]]]]] = None,
        sra_reports_access: typing.Optional[builtins.str] = None,
        usage_reports_access: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Role name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#name Role#name}
        :param analytics_access: Allow this role to view analytics. Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view reports produced by the same auth methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#analytics_access Role#analytics_access}
        :param assoc_auth_method: assoc_auth_method block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#assoc_auth_method Role#assoc_auth_method}
        :param audit_access: Allow this role to view audit logs. Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view audit logs produced by the same auth methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#audit_access Role#audit_access}
        :param delete_protection: Protection from accidental deletion of this role, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#delete_protection Role#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#description Role#description}
        :param event_center_access: Allow this role to view Event Center. Currently only 'none', 'own' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#event_center_access Role#event_center_access}
        :param event_forwarders_access: Allow this role to manage Event Forwarders. Currently only 'none' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#event_forwarders_access Role#event_forwarders_access}
        :param gw_analytics_access: Allow this role to view gw analytics. Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view reports produced by the same auth methods. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#gw_analytics_access Role#gw_analytics_access}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#id Role#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rules: rules block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#rules Role#rules}
        :param sra_reports_access: Allow this role to view SRA Clusters. Currently only 'none', 'own' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#sra_reports_access Role#sra_reports_access}
        :param usage_reports_access: Allow this role to view Usage reports. Currently only 'none' and 'all' values are supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#usage_reports_access Role#usage_reports_access}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de42e0907babd49e71b7f347a588a6ff2c01b5bbcb0a101350bf3ee881050c95)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument analytics_access", value=analytics_access, expected_type=type_hints["analytics_access"])
            check_type(argname="argument assoc_auth_method", value=assoc_auth_method, expected_type=type_hints["assoc_auth_method"])
            check_type(argname="argument audit_access", value=audit_access, expected_type=type_hints["audit_access"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument event_center_access", value=event_center_access, expected_type=type_hints["event_center_access"])
            check_type(argname="argument event_forwarders_access", value=event_forwarders_access, expected_type=type_hints["event_forwarders_access"])
            check_type(argname="argument gw_analytics_access", value=gw_analytics_access, expected_type=type_hints["gw_analytics_access"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rules", value=rules, expected_type=type_hints["rules"])
            check_type(argname="argument sra_reports_access", value=sra_reports_access, expected_type=type_hints["sra_reports_access"])
            check_type(argname="argument usage_reports_access", value=usage_reports_access, expected_type=type_hints["usage_reports_access"])
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
        if analytics_access is not None:
            self._values["analytics_access"] = analytics_access
        if assoc_auth_method is not None:
            self._values["assoc_auth_method"] = assoc_auth_method
        if audit_access is not None:
            self._values["audit_access"] = audit_access
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if event_center_access is not None:
            self._values["event_center_access"] = event_center_access
        if event_forwarders_access is not None:
            self._values["event_forwarders_access"] = event_forwarders_access
        if gw_analytics_access is not None:
            self._values["gw_analytics_access"] = gw_analytics_access
        if id is not None:
            self._values["id"] = id
        if rules is not None:
            self._values["rules"] = rules
        if sra_reports_access is not None:
            self._values["sra_reports_access"] = sra_reports_access
        if usage_reports_access is not None:
            self._values["usage_reports_access"] = usage_reports_access

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
        '''Role name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#name Role#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def analytics_access(self) -> typing.Optional[builtins.str]:
        '''Allow this role to view analytics.

        Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view reports produced by the same auth methods.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#analytics_access Role#analytics_access}
        '''
        result = self._values.get("analytics_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assoc_auth_method(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleAssocAuthMethod]]]:
        '''assoc_auth_method block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#assoc_auth_method Role#assoc_auth_method}
        '''
        result = self._values.get("assoc_auth_method")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleAssocAuthMethod]]], result)

    @builtins.property
    def audit_access(self) -> typing.Optional[builtins.str]:
        '''Allow this role to view audit logs.

        Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view audit logs produced by the same auth methods.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#audit_access Role#audit_access}
        '''
        result = self._values.get("audit_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this role, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#delete_protection Role#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#description Role#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_center_access(self) -> typing.Optional[builtins.str]:
        '''Allow this role to view Event Center. Currently only 'none', 'own' and 'all' values are supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#event_center_access Role#event_center_access}
        '''
        result = self._values.get("event_center_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_forwarders_access(self) -> typing.Optional[builtins.str]:
        '''Allow this role to manage Event Forwarders. Currently only 'none' and 'all' values are supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#event_forwarders_access Role#event_forwarders_access}
        '''
        result = self._values.get("event_forwarders_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gw_analytics_access(self) -> typing.Optional[builtins.str]:
        '''Allow this role to view gw analytics.

        Currently only 'none', 'own' and 'all' values are supported, allowing associated auth methods to view reports produced by the same auth methods.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#gw_analytics_access Role#gw_analytics_access}
        '''
        result = self._values.get("gw_analytics_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#id Role#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rules(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RoleRules"]]]:
        '''rules block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#rules Role#rules}
        '''
        result = self._values.get("rules")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RoleRules"]]], result)

    @builtins.property
    def sra_reports_access(self) -> typing.Optional[builtins.str]:
        '''Allow this role to view SRA Clusters. Currently only 'none', 'own' and 'all' values are supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#sra_reports_access Role#sra_reports_access}
        '''
        result = self._values.get("sra_reports_access")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usage_reports_access(self) -> typing.Optional[builtins.str]:
        '''Allow this role to view Usage reports. Currently only 'none' and 'all' values are supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#usage_reports_access Role#usage_reports_access}
        '''
        result = self._values.get("usage_reports_access")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.role.RoleRestrictedRules",
    jsii_struct_bases=[],
    name_mapping={},
)
class RoleRestrictedRules:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleRestrictedRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RoleRestrictedRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.role.RoleRestrictedRulesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beb2e651f5e25419c78dade70220ba31a56f65d689f316c8affda5c753e31301)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "RoleRestrictedRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__093ac5f0a1989d7022ad97d33d9617c07fa6c227de6d60248b6af5e494a9df0c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RoleRestrictedRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b5aa15eaf0187afa29153719876baf19a5eb9b3b39a53664b2f09e101d938e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9867d81378c6d906382c6be66720c2463bf33c4e79f64e0234cdd7798f4a1bfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d001c8306408c0131131b3033012e9247d8fdd581f1c7484d2456dd08401b8a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)


class RoleRestrictedRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.role.RoleRestrictedRulesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f02d61c9951059ab5b9e2c98fa031ae553a26c6315eb0011a54c687ee134028)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="capability")
    def capability(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "capability"))

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property
    @jsii.member(jsii_name="ruleType")
    def rule_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleType"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RoleRestrictedRules]:
        return typing.cast(typing.Optional[RoleRestrictedRules], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[RoleRestrictedRules]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb259acec5b5bec2909c11ccea151098267407ed82e8abafacce980ba569f045)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.role.RoleRules",
    jsii_struct_bases=[],
    name_mapping={"capability": "capability", "path": "path", "rule_type": "ruleType"},
)
class RoleRules:
    def __init__(
        self,
        *,
        capability: typing.Sequence[builtins.str],
        path: builtins.str,
        rule_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param capability: List of the approved/denied capabilities in the path options: [read, create, update, delete, list, deny] for sra-rule type: [allow_access, request_access, justify_access_only, approval_authority, upload_files, download_files]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#capability Role#capability}
        :param path: The path the rule refers to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#path Role#path}
        :param rule_type: item-rule, target-rule, role-rule, auth-method-rule, sra-rule. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#rule_type Role#rule_type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7d4db09967d84d8cfd4e8be826b5100a5e1d34191a97e3b485894441daa8e5c)
            check_type(argname="argument capability", value=capability, expected_type=type_hints["capability"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument rule_type", value=rule_type, expected_type=type_hints["rule_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "capability": capability,
            "path": path,
        }
        if rule_type is not None:
            self._values["rule_type"] = rule_type

    @builtins.property
    def capability(self) -> typing.List[builtins.str]:
        '''List of the approved/denied capabilities in the path options: [read, create, update, delete, list, deny] for sra-rule type: [allow_access, request_access, justify_access_only, approval_authority, upload_files, download_files].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#capability Role#capability}
        '''
        result = self._values.get("capability")
        assert result is not None, "Required property 'capability' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def path(self) -> builtins.str:
        '''The path the rule refers to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#path Role#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def rule_type(self) -> typing.Optional[builtins.str]:
        '''item-rule, target-rule, role-rule, auth-method-rule, sra-rule.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/role#rule_type Role#rule_type}
        '''
        result = self._values.get("rule_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RoleRules(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RoleRulesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.role.RoleRulesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6172d814fc844204bd869c395822855eb819ea1995a80955c981e3ffc2cdf89f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "RoleRulesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14c4df252c889fae2df2ee17c3bf176a72c8fdd77dfb48a13f7dd2cfa0e165ef)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RoleRulesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d6165d9bea16ac1d0d49cfb02794eda090d3836f44b3008d6e0ad2e4925852)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3554fdfdd83e3535172b08906cb56e09fbdf15997a628dc58330ec28231994f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b40182b8458339785ff9d09c3d351fc57564634f4548999bf6fd3376ddbb0b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleRules]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleRules]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleRules]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c88e712f473bfc44792a0b2116fb0a4eb6e3dbb9cd067b972a085fd4f6774c3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class RoleRulesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.role.RoleRulesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89d7fe6d81ff5ce610e1e22dd286d82cde4c9fcccb92549652c92880f81de322)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetRuleType")
    def reset_rule_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRuleType", []))

    @builtins.property
    @jsii.member(jsii_name="capabilityInput")
    def capability_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "capabilityInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="ruleTypeInput")
    def rule_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="capability")
    def capability(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "capability"))

    @capability.setter
    def capability(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__577e095ef2afe5bc7c8469225be7db66b07d669944921b92908cab8841642e1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "capability", value)

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__378759c20c9d1d2b992fa2726976573345d15b1e16dcb0fb7b25d3e6021d4046)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)

    @builtins.property
    @jsii.member(jsii_name="ruleType")
    def rule_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleType"))

    @rule_type.setter
    def rule_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbce3e90a49b4e8147b95c638185483610af708f7cb0c05309b19daeaf2d7a3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ruleType", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleRules]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleRules]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleRules]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__752d6e0e6d7c2838415313dff25fbc568198858232a1a900368ea634dec036c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "Role",
    "RoleAssocAuthMethod",
    "RoleAssocAuthMethodList",
    "RoleAssocAuthMethodOutputReference",
    "RoleConfig",
    "RoleRestrictedRules",
    "RoleRestrictedRulesList",
    "RoleRestrictedRulesOutputReference",
    "RoleRules",
    "RoleRulesList",
    "RoleRulesOutputReference",
]

publication.publish()

def _typecheckingstub__ad2fe649f53d40ca27c79c898c88c564c0f83369f7b100f2695e81cad85c97fb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    analytics_access: typing.Optional[builtins.str] = None,
    assoc_auth_method: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RoleAssocAuthMethod, typing.Dict[builtins.str, typing.Any]]]]] = None,
    audit_access: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    event_center_access: typing.Optional[builtins.str] = None,
    event_forwarders_access: typing.Optional[builtins.str] = None,
    gw_analytics_access: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RoleRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    sra_reports_access: typing.Optional[builtins.str] = None,
    usage_reports_access: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e4bd5e378a7d5a7c2d5b221d8871c30f71c4f8abb4eeb92f75b40110a0f04904(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7695cfb5994ac5f055ce8091f09dfa8eb76bff3504a3f8ba2b9dfae1099497a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RoleAssocAuthMethod, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ba235436d6c6c1956bd3c4c502d36e1b28b7b6e0709e63487ed417f0c23b03d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RoleRules, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa06cf4733203ea0ab8c596275ecb2b90aae02286b0bb5d5975c7e5a467c577e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71404befd0b09288f3c76f88fe7b52ce4965f8caa816568518cd21c460567683(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8909d6d9517e42a56089a72ffaea2e704846c06c592b7b75c1b11526ebf043f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11fcdd1956faf122780297b1247b6b9db9e6f4b0ca020db8533725055e1d1414(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccca3ebc764304f8d51acbec80ba515e68aeae3eaf2812de0f1196d93214ca50(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f016e4bf9bcff6195121b75cfa883ee1949e1580dfde57b124f9c3383170b741(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8731e95cf8b83b2598eeeb630a5ad50ddd4c0a34316482b98ca05a3bb3bed0d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81408afbf44be3bd59f3377acad0a456867606340f5d914e55a50b0149abb312(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32b80fec2414bb2e7fc5316ba8851bb35542235570d347ffcdbca921bf8c7c58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2596b75805e9dd78db5c90fa9c1f5377497ada7951179b6e11fb0b6c38f44b61(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b246e9f0b6835b4efcb2b404bf3ff54dbc38f47482f82931a2e0deb59bbd02b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbd5f8f2e3958da7c7749cff8e25e1ef5ce1269a3cdf6f7b83d1ad53ddd253cb(
    *,
    am_name: builtins.str,
    case_sensitive: typing.Optional[builtins.str] = None,
    sub_claims: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c43b6ff0e34e73976db336b88d1aebd5f968accf06e8ffc4706e4df946e7c571(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5aff2f008971595e3c3003df7bffc71334af68faf395c29680969ff74bbf139b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93638dca2672194822b511681a0ae627b96afe8e4eeff8435843cdd6ebbed72f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__166f9247f31d39425ef6e44d84da8cbab12f70124cb4306ff04aecd789fddefa(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59c3761885fed4862b565b80b802752d980a8292669f5ef7f0b68e8c603a83f1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6cbb395a05f212f42d779119538a81593bd9b3eb1d384d350727ede66f4af40(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleAssocAuthMethod]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a68595affb424b47134b643770af3e34227517f89a19e3131da09be726b01e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f40aff4da235114770412e41a76ac3e432c988ba6bc262566ae8123273397640(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8570511a68afcc50b24fcc1bd6ca243cddddc37adda71420df514b4bf7ed9869(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd47669bc36f35c1264f055774a0ccaac72ab56057d092b35747acb970fc3903(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd3a1ed58d360c7bb16048f50543608bda5fc9cd11768a172969acdb905358e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleAssocAuthMethod]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de42e0907babd49e71b7f347a588a6ff2c01b5bbcb0a101350bf3ee881050c95(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    analytics_access: typing.Optional[builtins.str] = None,
    assoc_auth_method: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RoleAssocAuthMethod, typing.Dict[builtins.str, typing.Any]]]]] = None,
    audit_access: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    event_center_access: typing.Optional[builtins.str] = None,
    event_forwarders_access: typing.Optional[builtins.str] = None,
    gw_analytics_access: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    rules: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RoleRules, typing.Dict[builtins.str, typing.Any]]]]] = None,
    sra_reports_access: typing.Optional[builtins.str] = None,
    usage_reports_access: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb2e651f5e25419c78dade70220ba31a56f65d689f316c8affda5c753e31301(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__093ac5f0a1989d7022ad97d33d9617c07fa6c227de6d60248b6af5e494a9df0c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b5aa15eaf0187afa29153719876baf19a5eb9b3b39a53664b2f09e101d938e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9867d81378c6d906382c6be66720c2463bf33c4e79f64e0234cdd7798f4a1bfc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d001c8306408c0131131b3033012e9247d8fdd581f1c7484d2456dd08401b8a7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f02d61c9951059ab5b9e2c98fa031ae553a26c6315eb0011a54c687ee134028(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb259acec5b5bec2909c11ccea151098267407ed82e8abafacce980ba569f045(
    value: typing.Optional[RoleRestrictedRules],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7d4db09967d84d8cfd4e8be826b5100a5e1d34191a97e3b485894441daa8e5c(
    *,
    capability: typing.Sequence[builtins.str],
    path: builtins.str,
    rule_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6172d814fc844204bd869c395822855eb819ea1995a80955c981e3ffc2cdf89f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14c4df252c889fae2df2ee17c3bf176a72c8fdd77dfb48a13f7dd2cfa0e165ef(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14d6165d9bea16ac1d0d49cfb02794eda090d3836f44b3008d6e0ad2e4925852(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3554fdfdd83e3535172b08906cb56e09fbdf15997a628dc58330ec28231994f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b40182b8458339785ff9d09c3d351fc57564634f4548999bf6fd3376ddbb0b2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c88e712f473bfc44792a0b2116fb0a4eb6e3dbb9cd067b972a085fd4f6774c3a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RoleRules]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89d7fe6d81ff5ce610e1e22dd286d82cde4c9fcccb92549652c92880f81de322(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__577e095ef2afe5bc7c8469225be7db66b07d669944921b92908cab8841642e1d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__378759c20c9d1d2b992fa2726976573345d15b1e16dcb0fb7b25d3e6021d4046(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbce3e90a49b4e8147b95c638185483610af708f7cb0c05309b19daeaf2d7a3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__752d6e0e6d7c2838415313dff25fbc568198858232a1a900368ea634dec036c0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, RoleRules]],
) -> None:
    """Type checking stubs"""
    pass
