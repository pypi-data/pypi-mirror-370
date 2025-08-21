'''
# `akeyless_auth_method_k8s`

Refer to the Terraform Registry for docs: [`akeyless_auth_method_k8s`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s).
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


class AuthMethodK8S(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethodK8S.AuthMethodK8S",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s akeyless_auth_method_k8s}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_pod_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_sa_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gen_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        public_key: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s akeyless_auth_method_k8s} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#name AuthMethodK8S#name}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#access_expires AuthMethodK8S#access_expires}
        :param audience: The audience in the Kubernetes JWT that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#audience AuthMethodK8S#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#audit_logs_claims AuthMethodK8S#audit_logs_claims}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_ips AuthMethodK8S#bound_ips}
        :param bound_namespaces: A list of namespaces that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_namespaces AuthMethodK8S#bound_namespaces}
        :param bound_pod_names: A list of pod names that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_pod_names AuthMethodK8S#bound_pod_names}
        :param bound_sa_names: A list of service account names that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_sa_names AuthMethodK8S#bound_sa_names}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#delete_protection AuthMethodK8S#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#force_sub_claims AuthMethodK8S#force_sub_claims}
        :param gen_key: If this flag is set to true, there is no need to manually provide a public key for the Kubernetes Auth Method, and instead, a key pair, will be generated as part of the command and the private part of the key will be returned (the private key is required for the K8S Auth Config in the Akeyless Gateway). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#gen_key AuthMethodK8S#gen_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#id AuthMethodK8S#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#jwt_ttl AuthMethodK8S#jwt_ttl}
        :param public_key: The generated public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#public_key AuthMethodK8S#public_key}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eae3d86876ee89dfa27b6f9b91e3f26abe9d24bf9dfc3a6ba6e9ec8f6cbed3d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodK8SConfig(
            name=name,
            access_expires=access_expires,
            audience=audience,
            audit_logs_claims=audit_logs_claims,
            bound_ips=bound_ips,
            bound_namespaces=bound_namespaces,
            bound_pod_names=bound_pod_names,
            bound_sa_names=bound_sa_names,
            delete_protection=delete_protection,
            force_sub_claims=force_sub_claims,
            gen_key=gen_key,
            id=id,
            jwt_ttl=jwt_ttl,
            public_key=public_key,
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
        '''Generates CDKTF code for importing a AuthMethodK8S resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethodK8S to import.
        :param import_from_id: The id of the existing AuthMethodK8S that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethodK8S to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89be6dd7b3e03cedffe7cb9f77d43f2d3ea200fbd9adca0d29ba2d6ff1da17f4)
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

    @jsii.member(jsii_name="resetBoundNamespaces")
    def reset_bound_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundNamespaces", []))

    @jsii.member(jsii_name="resetBoundPodNames")
    def reset_bound_pod_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundPodNames", []))

    @jsii.member(jsii_name="resetBoundSaNames")
    def reset_bound_sa_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundSaNames", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetForceSubClaims")
    def reset_force_sub_claims(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceSubClaims", []))

    @jsii.member(jsii_name="resetGenKey")
    def reset_gen_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJwtTtl")
    def reset_jwt_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtTtl", []))

    @jsii.member(jsii_name="resetPublicKey")
    def reset_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicKey", []))

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
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

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
    @jsii.member(jsii_name="boundNamespacesInput")
    def bound_namespaces_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundPodNamesInput")
    def bound_pod_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundPodNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundSaNamesInput")
    def bound_sa_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundSaNamesInput"))

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
    @jsii.member(jsii_name="genKeyInput")
    def gen_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "genKeyInput"))

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
    @jsii.member(jsii_name="publicKeyInput")
    def public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="accessExpires")
    def access_expires(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessExpires"))

    @access_expires.setter
    def access_expires(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d21b283d8b1ba98eb79fb70ef452db26ed37f5f61bec49601148ccd815197d17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c98548af84e5bb6df33d075a266b2daea89860d71fc9f611e07c9af884b7ec6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value)

    @builtins.property
    @jsii.member(jsii_name="auditLogsClaims")
    def audit_logs_claims(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "auditLogsClaims"))

    @audit_logs_claims.setter
    def audit_logs_claims(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__577127521f367682858340be35af794d0568dd6367f73dfbdc9619d1a929326b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "auditLogsClaims", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb84bb6a5119aa6c3b484412f1176058a258c3bdd27362d3c1c12ba0fef06991)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="boundNamespaces")
    def bound_namespaces(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundNamespaces"))

    @bound_namespaces.setter
    def bound_namespaces(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d235cee1df890e614ab552ad0c829006e044eba7878d4c3d2fd3cfcb52152c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundNamespaces", value)

    @builtins.property
    @jsii.member(jsii_name="boundPodNames")
    def bound_pod_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundPodNames"))

    @bound_pod_names.setter
    def bound_pod_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0c4ed88dad5ff9b0cf6688ec1ceac10adce8e954067077226dfb897c3200ef4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundPodNames", value)

    @builtins.property
    @jsii.member(jsii_name="boundSaNames")
    def bound_sa_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundSaNames"))

    @bound_sa_names.setter
    def bound_sa_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71cf0294cb1355a27faacf2feb21398764862c66eb2455600b0123c2c71b4b06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundSaNames", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d92e45999300d63249863c205b551853fa5e7b9ea6a0029dd55eea7291d221f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e5fc1d0db4c79ad204e769885f978079cb0ddd2d6fc75b3f45169598dbae2a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "forceSubClaims", value)

    @builtins.property
    @jsii.member(jsii_name="genKey")
    def gen_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "genKey"))

    @gen_key.setter
    def gen_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fd856a470a0f191d146e2d0f7db35430a5d1c0771aea16075c6d363df5fb83b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "genKey", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d113db030f86900ccb4f7f47601cb3ea96673b09ee7cdbb3a0678375de6693a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="jwtTtl")
    def jwt_ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "jwtTtl"))

    @jwt_ttl.setter
    def jwt_ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb170744823f835f5eff06f68a95ea4ad8fd986685e69b54aaf4b5068cfaab57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtTtl", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7b433ffdeeb2e6677aa176dafed58a4e757075728b23eb9ea34a9bf84fca15d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51024a280ffa820f88f712992d116ca7d890191ca5e5c3d56d245eab534c025d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicKey", value)


@jsii.data_type(
    jsii_type="akeyless.authMethodK8S.AuthMethodK8SConfig",
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
        "audience": "audience",
        "audit_logs_claims": "auditLogsClaims",
        "bound_ips": "boundIps",
        "bound_namespaces": "boundNamespaces",
        "bound_pod_names": "boundPodNames",
        "bound_sa_names": "boundSaNames",
        "delete_protection": "deleteProtection",
        "force_sub_claims": "forceSubClaims",
        "gen_key": "genKey",
        "id": "id",
        "jwt_ttl": "jwtTtl",
        "public_key": "publicKey",
    },
)
class AuthMethodK8SConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        audience: typing.Optional[builtins.str] = None,
        audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_pod_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_sa_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        gen_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_ttl: typing.Optional[jsii.Number] = None,
        public_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Auth Method name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#name AuthMethodK8S#name}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#access_expires AuthMethodK8S#access_expires}
        :param audience: The audience in the Kubernetes JWT that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#audience AuthMethodK8S#audience}
        :param audit_logs_claims: Subclaims to include in audit logs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#audit_logs_claims AuthMethodK8S#audit_logs_claims}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_ips AuthMethodK8S#bound_ips}
        :param bound_namespaces: A list of namespaces that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_namespaces AuthMethodK8S#bound_namespaces}
        :param bound_pod_names: A list of pod names that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_pod_names AuthMethodK8S#bound_pod_names}
        :param bound_sa_names: A list of service account names that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_sa_names AuthMethodK8S#bound_sa_names}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#delete_protection AuthMethodK8S#delete_protection}
        :param force_sub_claims: enforce role-association must include sub claims. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#force_sub_claims AuthMethodK8S#force_sub_claims}
        :param gen_key: If this flag is set to true, there is no need to manually provide a public key for the Kubernetes Auth Method, and instead, a key pair, will be generated as part of the command and the private part of the key will be returned (the private key is required for the K8S Auth Config in the Akeyless Gateway). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#gen_key AuthMethodK8S#gen_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#id AuthMethodK8S#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_ttl: Creds expiration time in minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#jwt_ttl AuthMethodK8S#jwt_ttl}
        :param public_key: The generated public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#public_key AuthMethodK8S#public_key}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c31ccd40a6872b2a58db42d90c9c4783f58b1091241bd5803838d00da94b449)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument access_expires", value=access_expires, expected_type=type_hints["access_expires"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument audit_logs_claims", value=audit_logs_claims, expected_type=type_hints["audit_logs_claims"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument bound_namespaces", value=bound_namespaces, expected_type=type_hints["bound_namespaces"])
            check_type(argname="argument bound_pod_names", value=bound_pod_names, expected_type=type_hints["bound_pod_names"])
            check_type(argname="argument bound_sa_names", value=bound_sa_names, expected_type=type_hints["bound_sa_names"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument force_sub_claims", value=force_sub_claims, expected_type=type_hints["force_sub_claims"])
            check_type(argname="argument gen_key", value=gen_key, expected_type=type_hints["gen_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jwt_ttl", value=jwt_ttl, expected_type=type_hints["jwt_ttl"])
            check_type(argname="argument public_key", value=public_key, expected_type=type_hints["public_key"])
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
        if audience is not None:
            self._values["audience"] = audience
        if audit_logs_claims is not None:
            self._values["audit_logs_claims"] = audit_logs_claims
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if bound_namespaces is not None:
            self._values["bound_namespaces"] = bound_namespaces
        if bound_pod_names is not None:
            self._values["bound_pod_names"] = bound_pod_names
        if bound_sa_names is not None:
            self._values["bound_sa_names"] = bound_sa_names
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if force_sub_claims is not None:
            self._values["force_sub_claims"] = force_sub_claims
        if gen_key is not None:
            self._values["gen_key"] = gen_key
        if id is not None:
            self._values["id"] = id
        if jwt_ttl is not None:
            self._values["jwt_ttl"] = jwt_ttl
        if public_key is not None:
            self._values["public_key"] = public_key

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#name AuthMethodK8S#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#access_expires AuthMethodK8S#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''The audience in the Kubernetes JWT that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#audience AuthMethodK8S#audience}
        '''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def audit_logs_claims(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Subclaims to include in audit logs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#audit_logs_claims AuthMethodK8S#audit_logs_claims}
        '''
        result = self._values.get("audit_logs_claims")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A CIDR whitelist with the IPs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_ips AuthMethodK8S#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_namespaces(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of namespaces that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_namespaces AuthMethodK8S#bound_namespaces}
        '''
        result = self._values.get("bound_namespaces")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_pod_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of pod names that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_pod_names AuthMethodK8S#bound_pod_names}
        '''
        result = self._values.get("bound_pod_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_sa_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of service account names that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#bound_sa_names AuthMethodK8S#bound_sa_names}
        '''
        result = self._values.get("bound_sa_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this auth method, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#delete_protection AuthMethodK8S#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_sub_claims(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''enforce role-association must include sub claims.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#force_sub_claims AuthMethodK8S#force_sub_claims}
        '''
        result = self._values.get("force_sub_claims")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def gen_key(self) -> typing.Optional[builtins.str]:
        '''If this flag is set to true, there is no need to manually provide a public key for the Kubernetes Auth Method, and instead, a key pair, will be generated as part of the command and the private part of the key will be returned (the private key is required for the K8S Auth Config in the Akeyless Gateway).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#gen_key AuthMethodK8S#gen_key}
        '''
        result = self._values.get("gen_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#id AuthMethodK8S#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_ttl(self) -> typing.Optional[jsii.Number]:
        '''Creds expiration time in minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#jwt_ttl AuthMethodK8S#jwt_ttl}
        '''
        result = self._values.get("jwt_ttl")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def public_key(self) -> typing.Optional[builtins.str]:
        '''The generated public key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method_k8s#public_key AuthMethodK8S#public_key}
        '''
        result = self._values.get("public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodK8SConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuthMethodK8S",
    "AuthMethodK8SConfig",
]

publication.publish()

def _typecheckingstub__5eae3d86876ee89dfa27b6f9b91e3f26abe9d24bf9dfc3a6ba6e9ec8f6cbed3d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_pod_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_sa_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gen_key: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    public_key: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__89be6dd7b3e03cedffe7cb9f77d43f2d3ea200fbd9adca0d29ba2d6ff1da17f4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d21b283d8b1ba98eb79fb70ef452db26ed37f5f61bec49601148ccd815197d17(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c98548af84e5bb6df33d075a266b2daea89860d71fc9f611e07c9af884b7ec6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__577127521f367682858340be35af794d0568dd6367f73dfbdc9619d1a929326b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb84bb6a5119aa6c3b484412f1176058a258c3bdd27362d3c1c12ba0fef06991(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d235cee1df890e614ab552ad0c829006e044eba7878d4c3d2fd3cfcb52152c6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0c4ed88dad5ff9b0cf6688ec1ceac10adce8e954067077226dfb897c3200ef4(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71cf0294cb1355a27faacf2feb21398764862c66eb2455600b0123c2c71b4b06(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d92e45999300d63249863c205b551853fa5e7b9ea6a0029dd55eea7291d221f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e5fc1d0db4c79ad204e769885f978079cb0ddd2d6fc75b3f45169598dbae2a8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fd856a470a0f191d146e2d0f7db35430a5d1c0771aea16075c6d363df5fb83b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d113db030f86900ccb4f7f47601cb3ea96673b09ee7cdbb3a0678375de6693a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb170744823f835f5eff06f68a95ea4ad8fd986685e69b54aaf4b5068cfaab57(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7b433ffdeeb2e6677aa176dafed58a4e757075728b23eb9ea34a9bf84fca15d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51024a280ffa820f88f712992d116ca7d890191ca5e5c3d56d245eab534c025d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c31ccd40a6872b2a58db42d90c9c4783f58b1091241bd5803838d00da94b449(
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
    audience: typing.Optional[builtins.str] = None,
    audit_logs_claims: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_ips: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_namespaces: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_pod_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_sa_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    force_sub_claims: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    gen_key: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_ttl: typing.Optional[jsii.Number] = None,
    public_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
