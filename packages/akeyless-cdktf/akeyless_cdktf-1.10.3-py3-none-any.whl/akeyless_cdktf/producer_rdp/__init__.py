'''
# `akeyless_producer_rdp`

Refer to the Terraform Registry for docs: [`akeyless_producer_rdp`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp).
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


class ProducerRdp(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerRdp.ProducerRdp",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp akeyless_producer_rdp}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        fixed_user_only: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        rdp_admin_name: typing.Optional[builtins.str] = None,
        rdp_admin_pwd: typing.Optional[builtins.str] = None,
        rdp_host_name: typing.Optional[builtins.str] = None,
        rdp_host_port: typing.Optional[builtins.str] = None,
        rdp_user_groups: typing.Optional[builtins.str] = None,
        secure_access_allow_external_user: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_rdp_domain: typing.Optional[builtins.str] = None,
        secure_access_rdp_user: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        user_ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp akeyless_producer_rdp} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#name ProducerRdp#name}
        :param fixed_user_only: Enable fixed user only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#fixed_user_only ProducerRdp#fixed_user_only}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#id ProducerRdp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#producer_encryption_key_name ProducerRdp#producer_encryption_key_name}
        :param rdp_admin_name: RDP Admin name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_admin_name ProducerRdp#rdp_admin_name}
        :param rdp_admin_pwd: RDP Admin Password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_admin_pwd ProducerRdp#rdp_admin_pwd}
        :param rdp_host_name: RDP Host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_host_name ProducerRdp#rdp_host_name}
        :param rdp_host_port: RDP Host port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_host_port ProducerRdp#rdp_host_port}
        :param rdp_user_groups: RDP UserGroup name(s). Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_user_groups ProducerRdp#rdp_user_groups}
        :param secure_access_allow_external_user: Allow providing external user for a domain users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_allow_external_user ProducerRdp#secure_access_allow_external_user}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_enable ProducerRdp#secure_access_enable}
        :param secure_access_host: Target servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_host ProducerRdp#secure_access_host}
        :param secure_access_rdp_domain: Required when the Dynamic Secret is used for a domain user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_rdp_domain ProducerRdp#secure_access_rdp_domain}
        :param secure_access_rdp_user: Override the RDP Domain username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_rdp_user ProducerRdp#secure_access_rdp_user}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_web ProducerRdp#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#tags ProducerRdp#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#target_name ProducerRdp#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#user_ttl ProducerRdp#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbd87efdb34f6b7e4cd04f9ba426715c2381bb2a73e2cfd82b87c97ffec067bb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerRdpConfig(
            name=name,
            fixed_user_only=fixed_user_only,
            id=id,
            producer_encryption_key_name=producer_encryption_key_name,
            rdp_admin_name=rdp_admin_name,
            rdp_admin_pwd=rdp_admin_pwd,
            rdp_host_name=rdp_host_name,
            rdp_host_port=rdp_host_port,
            rdp_user_groups=rdp_user_groups,
            secure_access_allow_external_user=secure_access_allow_external_user,
            secure_access_enable=secure_access_enable,
            secure_access_host=secure_access_host,
            secure_access_rdp_domain=secure_access_rdp_domain,
            secure_access_rdp_user=secure_access_rdp_user,
            secure_access_web=secure_access_web,
            tags=tags,
            target_name=target_name,
            user_ttl=user_ttl,
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
        '''Generates CDKTF code for importing a ProducerRdp resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerRdp to import.
        :param import_from_id: The id of the existing ProducerRdp that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerRdp to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0980c3d34c41541516863b4160efb7390a2d6ccf353f40877251b681bddf8bf3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetFixedUserOnly")
    def reset_fixed_user_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFixedUserOnly", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

    @jsii.member(jsii_name="resetRdpAdminName")
    def reset_rdp_admin_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpAdminName", []))

    @jsii.member(jsii_name="resetRdpAdminPwd")
    def reset_rdp_admin_pwd(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpAdminPwd", []))

    @jsii.member(jsii_name="resetRdpHostName")
    def reset_rdp_host_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpHostName", []))

    @jsii.member(jsii_name="resetRdpHostPort")
    def reset_rdp_host_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpHostPort", []))

    @jsii.member(jsii_name="resetRdpUserGroups")
    def reset_rdp_user_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpUserGroups", []))

    @jsii.member(jsii_name="resetSecureAccessAllowExternalUser")
    def reset_secure_access_allow_external_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessAllowExternalUser", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

    @jsii.member(jsii_name="resetSecureAccessHost")
    def reset_secure_access_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessHost", []))

    @jsii.member(jsii_name="resetSecureAccessRdpDomain")
    def reset_secure_access_rdp_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessRdpDomain", []))

    @jsii.member(jsii_name="resetSecureAccessRdpUser")
    def reset_secure_access_rdp_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessRdpUser", []))

    @jsii.member(jsii_name="resetSecureAccessWeb")
    def reset_secure_access_web(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWeb", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTargetName")
    def reset_target_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetName", []))

    @jsii.member(jsii_name="resetUserTtl")
    def reset_user_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserTtl", []))

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
    @jsii.member(jsii_name="fixedUserOnlyInput")
    def fixed_user_only_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fixedUserOnlyInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyNameInput")
    def producer_encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "producerEncryptionKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpAdminNameInput")
    def rdp_admin_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpAdminNameInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpAdminPwdInput")
    def rdp_admin_pwd_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpAdminPwdInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpHostNameInput")
    def rdp_host_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpHostNameInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpHostPortInput")
    def rdp_host_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpHostPortInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpUserGroupsInput")
    def rdp_user_groups_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpUserGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessAllowExternalUserInput")
    def secure_access_allow_external_user_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessAllowExternalUserInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessHostInput")
    def secure_access_host_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "secureAccessHostInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessRdpDomainInput")
    def secure_access_rdp_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessRdpDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessRdpUserInput")
    def secure_access_rdp_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessRdpUserInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessWebInput")
    def secure_access_web_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessWebInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userTtlInput")
    def user_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="fixedUserOnly")
    def fixed_user_only(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fixedUserOnly"))

    @fixed_user_only.setter
    def fixed_user_only(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08239f8876ad1c3424954f15645e37d87c85b3a9c6356e3452bdb41f54bbbb40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fixedUserOnly", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06dd9d4f3fc0fe221aa38d8fde285adf76576cc59462281ff98ac48d3295576b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f872466a095779bb8515704650568b274ebde66ced8f4a14d691e842bbd0415)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c13bcf50737c4089aa561901fe3a9a19624c29e0d82031fb8883374d017238fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="rdpAdminName")
    def rdp_admin_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpAdminName"))

    @rdp_admin_name.setter
    def rdp_admin_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__204858ea0457992b90f890cf10f3625152235ea74e2e04b86bf1f5ee00e068b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpAdminName", value)

    @builtins.property
    @jsii.member(jsii_name="rdpAdminPwd")
    def rdp_admin_pwd(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpAdminPwd"))

    @rdp_admin_pwd.setter
    def rdp_admin_pwd(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a0c512b1a18f1e04e3105f88342f815e7636b71da8a4d6914652698907dcca3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpAdminPwd", value)

    @builtins.property
    @jsii.member(jsii_name="rdpHostName")
    def rdp_host_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpHostName"))

    @rdp_host_name.setter
    def rdp_host_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbdf361cd9bfa1787c8c751a63e9519169206147315a5c9bc11e13850bc92858)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpHostName", value)

    @builtins.property
    @jsii.member(jsii_name="rdpHostPort")
    def rdp_host_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpHostPort"))

    @rdp_host_port.setter
    def rdp_host_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4360ca6e0af424e7daebbbf8efa06b3d3dd3d727fc66cf1a6c0718d32d952209)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpHostPort", value)

    @builtins.property
    @jsii.member(jsii_name="rdpUserGroups")
    def rdp_user_groups(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpUserGroups"))

    @rdp_user_groups.setter
    def rdp_user_groups(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fd6239a36bd831e6280bc842b199b1dcbc8e03542b21079bfcf4b190add981e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpUserGroups", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessAllowExternalUser")
    def secure_access_allow_external_user(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessAllowExternalUser"))

    @secure_access_allow_external_user.setter
    def secure_access_allow_external_user(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a73165c0897ee58ad61a71f086256063495259fb1ad23b00a8df4cd2c690ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAllowExternalUser", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0dd1622b6f36aaf729e85913d434f70eb8fec2ebb82f857e07ca5bacd0fa8bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e26196e20e013768b18110cc8e875fd727e35a0770f996bf45c595633d30f99a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessHost", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessRdpDomain")
    def secure_access_rdp_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessRdpDomain"))

    @secure_access_rdp_domain.setter
    def secure_access_rdp_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3cfbf2b1ba9c5a6db5753858f974f4f9cfb9ea5ebb69adf2f70bfe3be82f86e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessRdpDomain", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessRdpUser")
    def secure_access_rdp_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessRdpUser"))

    @secure_access_rdp_user.setter
    def secure_access_rdp_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09b17c9e87aa061eac66053ae0da72eae6d7775a0384289c0a77479ff147a89b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessRdpUser", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessWeb")
    def secure_access_web(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessWeb"))

    @secure_access_web.setter
    def secure_access_web(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9246988a66a4ce2742ee1fa47b73f08cbdd303ae6c69fa343a5f7de226d6e7e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01611ed190af6ca041e057fc1a998b0474ec6de84e9e8c391ef009cfb9471a57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8397e1850fe3c410b9dddaa43f30ff7b69dfbb993c2a8e13a9556e17868a1aa3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92029b09fe57545f5336a3f96cded1da90f34e993725e96683e71c6fb476e95a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerRdp.ProducerRdpConfig",
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
        "fixed_user_only": "fixedUserOnly",
        "id": "id",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "rdp_admin_name": "rdpAdminName",
        "rdp_admin_pwd": "rdpAdminPwd",
        "rdp_host_name": "rdpHostName",
        "rdp_host_port": "rdpHostPort",
        "rdp_user_groups": "rdpUserGroups",
        "secure_access_allow_external_user": "secureAccessAllowExternalUser",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_host": "secureAccessHost",
        "secure_access_rdp_domain": "secureAccessRdpDomain",
        "secure_access_rdp_user": "secureAccessRdpUser",
        "secure_access_web": "secureAccessWeb",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerRdpConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        fixed_user_only: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        rdp_admin_name: typing.Optional[builtins.str] = None,
        rdp_admin_pwd: typing.Optional[builtins.str] = None,
        rdp_host_name: typing.Optional[builtins.str] = None,
        rdp_host_port: typing.Optional[builtins.str] = None,
        rdp_user_groups: typing.Optional[builtins.str] = None,
        secure_access_allow_external_user: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_rdp_domain: typing.Optional[builtins.str] = None,
        secure_access_rdp_user: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        user_ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#name ProducerRdp#name}
        :param fixed_user_only: Enable fixed user only. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#fixed_user_only ProducerRdp#fixed_user_only}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#id ProducerRdp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#producer_encryption_key_name ProducerRdp#producer_encryption_key_name}
        :param rdp_admin_name: RDP Admin name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_admin_name ProducerRdp#rdp_admin_name}
        :param rdp_admin_pwd: RDP Admin Password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_admin_pwd ProducerRdp#rdp_admin_pwd}
        :param rdp_host_name: RDP Host name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_host_name ProducerRdp#rdp_host_name}
        :param rdp_host_port: RDP Host port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_host_port ProducerRdp#rdp_host_port}
        :param rdp_user_groups: RDP UserGroup name(s). Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_user_groups ProducerRdp#rdp_user_groups}
        :param secure_access_allow_external_user: Allow providing external user for a domain users. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_allow_external_user ProducerRdp#secure_access_allow_external_user}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_enable ProducerRdp#secure_access_enable}
        :param secure_access_host: Target servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_host ProducerRdp#secure_access_host}
        :param secure_access_rdp_domain: Required when the Dynamic Secret is used for a domain user. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_rdp_domain ProducerRdp#secure_access_rdp_domain}
        :param secure_access_rdp_user: Override the RDP Domain username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_rdp_user ProducerRdp#secure_access_rdp_user}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_web ProducerRdp#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#tags ProducerRdp#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#target_name ProducerRdp#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#user_ttl ProducerRdp#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4f54ffb1f6650fda31fd11903a2ad2886a7e4630c5e196902455a516c2006f1)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument fixed_user_only", value=fixed_user_only, expected_type=type_hints["fixed_user_only"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
            check_type(argname="argument rdp_admin_name", value=rdp_admin_name, expected_type=type_hints["rdp_admin_name"])
            check_type(argname="argument rdp_admin_pwd", value=rdp_admin_pwd, expected_type=type_hints["rdp_admin_pwd"])
            check_type(argname="argument rdp_host_name", value=rdp_host_name, expected_type=type_hints["rdp_host_name"])
            check_type(argname="argument rdp_host_port", value=rdp_host_port, expected_type=type_hints["rdp_host_port"])
            check_type(argname="argument rdp_user_groups", value=rdp_user_groups, expected_type=type_hints["rdp_user_groups"])
            check_type(argname="argument secure_access_allow_external_user", value=secure_access_allow_external_user, expected_type=type_hints["secure_access_allow_external_user"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_host", value=secure_access_host, expected_type=type_hints["secure_access_host"])
            check_type(argname="argument secure_access_rdp_domain", value=secure_access_rdp_domain, expected_type=type_hints["secure_access_rdp_domain"])
            check_type(argname="argument secure_access_rdp_user", value=secure_access_rdp_user, expected_type=type_hints["secure_access_rdp_user"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument target_name", value=target_name, expected_type=type_hints["target_name"])
            check_type(argname="argument user_ttl", value=user_ttl, expected_type=type_hints["user_ttl"])
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
        if fixed_user_only is not None:
            self._values["fixed_user_only"] = fixed_user_only
        if id is not None:
            self._values["id"] = id
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
        if rdp_admin_name is not None:
            self._values["rdp_admin_name"] = rdp_admin_name
        if rdp_admin_pwd is not None:
            self._values["rdp_admin_pwd"] = rdp_admin_pwd
        if rdp_host_name is not None:
            self._values["rdp_host_name"] = rdp_host_name
        if rdp_host_port is not None:
            self._values["rdp_host_port"] = rdp_host_port
        if rdp_user_groups is not None:
            self._values["rdp_user_groups"] = rdp_user_groups
        if secure_access_allow_external_user is not None:
            self._values["secure_access_allow_external_user"] = secure_access_allow_external_user
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_host is not None:
            self._values["secure_access_host"] = secure_access_host
        if secure_access_rdp_domain is not None:
            self._values["secure_access_rdp_domain"] = secure_access_rdp_domain
        if secure_access_rdp_user is not None:
            self._values["secure_access_rdp_user"] = secure_access_rdp_user
        if secure_access_web is not None:
            self._values["secure_access_web"] = secure_access_web
        if tags is not None:
            self._values["tags"] = tags
        if target_name is not None:
            self._values["target_name"] = target_name
        if user_ttl is not None:
            self._values["user_ttl"] = user_ttl

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
        '''Producer name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#name ProducerRdp#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def fixed_user_only(self) -> typing.Optional[builtins.str]:
        '''Enable fixed user only.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#fixed_user_only ProducerRdp#fixed_user_only}
        '''
        result = self._values.get("fixed_user_only")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#id ProducerRdp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#producer_encryption_key_name ProducerRdp#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_admin_name(self) -> typing.Optional[builtins.str]:
        '''RDP Admin name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_admin_name ProducerRdp#rdp_admin_name}
        '''
        result = self._values.get("rdp_admin_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_admin_pwd(self) -> typing.Optional[builtins.str]:
        '''RDP Admin Password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_admin_pwd ProducerRdp#rdp_admin_pwd}
        '''
        result = self._values.get("rdp_admin_pwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_host_name(self) -> typing.Optional[builtins.str]:
        '''RDP Host name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_host_name ProducerRdp#rdp_host_name}
        '''
        result = self._values.get("rdp_host_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_host_port(self) -> typing.Optional[builtins.str]:
        '''RDP Host port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_host_port ProducerRdp#rdp_host_port}
        '''
        result = self._values.get("rdp_host_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_user_groups(self) -> typing.Optional[builtins.str]:
        '''RDP UserGroup name(s). Multiple values should be separated by comma.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#rdp_user_groups ProducerRdp#rdp_user_groups}
        '''
        result = self._values.get("rdp_user_groups")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_allow_external_user(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Allow providing external user for a domain users.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_allow_external_user ProducerRdp#secure_access_allow_external_user}
        '''
        result = self._values.get("secure_access_allow_external_user")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_enable ProducerRdp#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target servers for connections., For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_host ProducerRdp#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_rdp_domain(self) -> typing.Optional[builtins.str]:
        '''Required when the Dynamic Secret is used for a domain user.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_rdp_domain ProducerRdp#secure_access_rdp_domain}
        '''
        result = self._values.get("secure_access_rdp_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_rdp_user(self) -> typing.Optional[builtins.str]:
        '''Override the RDP Domain username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_rdp_user ProducerRdp#secure_access_rdp_user}
        '''
        result = self._values.get("secure_access_rdp_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#secure_access_web ProducerRdp#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#tags ProducerRdp#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#target_name ProducerRdp#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_rdp#user_ttl ProducerRdp#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerRdpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerRdp",
    "ProducerRdpConfig",
]

publication.publish()

def _typecheckingstub__dbd87efdb34f6b7e4cd04f9ba426715c2381bb2a73e2cfd82b87c97ffec067bb(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    fixed_user_only: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    rdp_admin_name: typing.Optional[builtins.str] = None,
    rdp_admin_pwd: typing.Optional[builtins.str] = None,
    rdp_host_name: typing.Optional[builtins.str] = None,
    rdp_host_port: typing.Optional[builtins.str] = None,
    rdp_user_groups: typing.Optional[builtins.str] = None,
    secure_access_allow_external_user: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_rdp_domain: typing.Optional[builtins.str] = None,
    secure_access_rdp_user: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__0980c3d34c41541516863b4160efb7390a2d6ccf353f40877251b681bddf8bf3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08239f8876ad1c3424954f15645e37d87c85b3a9c6356e3452bdb41f54bbbb40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06dd9d4f3fc0fe221aa38d8fde285adf76576cc59462281ff98ac48d3295576b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f872466a095779bb8515704650568b274ebde66ced8f4a14d691e842bbd0415(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c13bcf50737c4089aa561901fe3a9a19624c29e0d82031fb8883374d017238fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__204858ea0457992b90f890cf10f3625152235ea74e2e04b86bf1f5ee00e068b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a0c512b1a18f1e04e3105f88342f815e7636b71da8a4d6914652698907dcca3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbdf361cd9bfa1787c8c751a63e9519169206147315a5c9bc11e13850bc92858(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4360ca6e0af424e7daebbbf8efa06b3d3dd3d727fc66cf1a6c0718d32d952209(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd6239a36bd831e6280bc842b199b1dcbc8e03542b21079bfcf4b190add981e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a73165c0897ee58ad61a71f086256063495259fb1ad23b00a8df4cd2c690ec(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0dd1622b6f36aaf729e85913d434f70eb8fec2ebb82f857e07ca5bacd0fa8bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e26196e20e013768b18110cc8e875fd727e35a0770f996bf45c595633d30f99a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3cfbf2b1ba9c5a6db5753858f974f4f9cfb9ea5ebb69adf2f70bfe3be82f86e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09b17c9e87aa061eac66053ae0da72eae6d7775a0384289c0a77479ff147a89b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9246988a66a4ce2742ee1fa47b73f08cbdd303ae6c69fa343a5f7de226d6e7e7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01611ed190af6ca041e057fc1a998b0474ec6de84e9e8c391ef009cfb9471a57(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8397e1850fe3c410b9dddaa43f30ff7b69dfbb993c2a8e13a9556e17868a1aa3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92029b09fe57545f5336a3f96cded1da90f34e993725e96683e71c6fb476e95a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4f54ffb1f6650fda31fd11903a2ad2886a7e4630c5e196902455a516c2006f1(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    fixed_user_only: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    rdp_admin_name: typing.Optional[builtins.str] = None,
    rdp_admin_pwd: typing.Optional[builtins.str] = None,
    rdp_host_name: typing.Optional[builtins.str] = None,
    rdp_host_port: typing.Optional[builtins.str] = None,
    rdp_user_groups: typing.Optional[builtins.str] = None,
    secure_access_allow_external_user: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_rdp_domain: typing.Optional[builtins.str] = None,
    secure_access_rdp_user: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
