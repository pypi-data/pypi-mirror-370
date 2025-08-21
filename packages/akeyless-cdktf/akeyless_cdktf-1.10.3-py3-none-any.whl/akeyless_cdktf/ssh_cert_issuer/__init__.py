'''
# `akeyless_ssh_cert_issuer`

Refer to the Terraform Registry for docs: [`akeyless_ssh_cert_issuer`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer).
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


class SshCertIssuer(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.sshCertIssuer.SshCertIssuer",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer akeyless_ssh_cert_issuer}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        allowed_users: builtins.str,
        name: builtins.str,
        signer_key_name: builtins.str,
        ttl: jsii.Number,
        delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        principals: typing.Optional[builtins.str] = None,
        secure_access_bastion_api: typing.Optional[builtins.str] = None,
        secure_access_bastion_ssh: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_ssh_creds_user: typing.Optional[builtins.str] = None,
        secure_access_use_internal_bastion: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer akeyless_ssh_cert_issuer} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allowed_users: Users allowed to fetch the certificate, e.g root,ubuntu. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#allowed_users SshCertIssuer#allowed_users}
        :param name: SSH certificate issuer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#name SshCertIssuer#name}
        :param signer_key_name: A key to sign the certificate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#signer_key_name SshCertIssuer#signer_key_name}
        :param ttl: The requested Time To Live for the certificate, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#ttl SshCertIssuer#ttl}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#delete_protection SshCertIssuer#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#description SshCertIssuer#description}
        :param extensions: Signed certificates with extensions (key/val), e.g permit-port-forwarding=. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#extensions SshCertIssuer#extensions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#id SshCertIssuer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param principals: Signed certificates with principal, e.g example_role1,example_role2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#principals SshCertIssuer#principals}
        :param secure_access_bastion_api: Bastion's SSH control API endpoint. E.g. https://my.bastion:9900. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_bastion_api SshCertIssuer#secure_access_bastion_api}
        :param secure_access_bastion_ssh: Bastion's SSH server. E.g. my.bastion:22. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_bastion_ssh SshCertIssuer#secure_access_bastion_ssh}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_enable SshCertIssuer#secure_access_enable}
        :param secure_access_host: Target servers for connections. (In case of Linked Target association, host(s) will inherit Linked Target hosts - Relevant only for Dynamic Secrets/producers) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_host SshCertIssuer#secure_access_host}
        :param secure_access_ssh_creds_user: SSH username to connect to target server, must be in 'Allowed Users' list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_ssh_creds_user SshCertIssuer#secure_access_ssh_creds_user}
        :param secure_access_use_internal_bastion: Use internal SSH Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_use_internal_bastion SshCertIssuer#secure_access_use_internal_bastion}
        :param tags: List of the tags attached to this key. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#tags SshCertIssuer#tags}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ab6801d9809be063348fa5ab7a1d2c7dc0538767c6da011faba0e813715c878)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = SshCertIssuerConfig(
            allowed_users=allowed_users,
            name=name,
            signer_key_name=signer_key_name,
            ttl=ttl,
            delete_protection=delete_protection,
            description=description,
            extensions=extensions,
            id=id,
            principals=principals,
            secure_access_bastion_api=secure_access_bastion_api,
            secure_access_bastion_ssh=secure_access_bastion_ssh,
            secure_access_enable=secure_access_enable,
            secure_access_host=secure_access_host,
            secure_access_ssh_creds_user=secure_access_ssh_creds_user,
            secure_access_use_internal_bastion=secure_access_use_internal_bastion,
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
        '''Generates CDKTF code for importing a SshCertIssuer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the SshCertIssuer to import.
        :param import_from_id: The id of the existing SshCertIssuer that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the SshCertIssuer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a22f09cc76449786e7b9affe402ce4422cf91514ee547c19a753a54863a9aa9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetExtensions")
    def reset_extensions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExtensions", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPrincipals")
    def reset_principals(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrincipals", []))

    @jsii.member(jsii_name="resetSecureAccessBastionApi")
    def reset_secure_access_bastion_api(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessBastionApi", []))

    @jsii.member(jsii_name="resetSecureAccessBastionSsh")
    def reset_secure_access_bastion_ssh(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessBastionSsh", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

    @jsii.member(jsii_name="resetSecureAccessHost")
    def reset_secure_access_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessHost", []))

    @jsii.member(jsii_name="resetSecureAccessSshCredsUser")
    def reset_secure_access_ssh_creds_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessSshCredsUser", []))

    @jsii.member(jsii_name="resetSecureAccessUseInternalBastion")
    def reset_secure_access_use_internal_bastion(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessUseInternalBastion", []))

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
    @jsii.member(jsii_name="allowedUsersInput")
    def allowed_users_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "allowedUsersInput"))

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
    @jsii.member(jsii_name="extensionsInput")
    def extensions_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "extensionsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="principalsInput")
    def principals_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "principalsInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionApiInput")
    def secure_access_bastion_api_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessBastionApiInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionSshInput")
    def secure_access_bastion_ssh_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessBastionSshInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessHostInput")
    def secure_access_host_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "secureAccessHostInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessSshCredsUserInput")
    def secure_access_ssh_creds_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessSshCredsUserInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessUseInternalBastionInput")
    def secure_access_use_internal_bastion_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessUseInternalBastionInput"))

    @builtins.property
    @jsii.member(jsii_name="signerKeyNameInput")
    def signer_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signerKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="allowedUsers")
    def allowed_users(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "allowedUsers"))

    @allowed_users.setter
    def allowed_users(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6dd2e0d3d713739f8683186320045cfc270b18f0f3e6307dffd34f25d1510ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowedUsers", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__3755bd8c34b294b59c3043515b6ef25e63c713c7eae3245f0d596df7428192d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36883315a5cb4df62872c21b9782dd51864a228693430c453164e4905f6e7928)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="extensions")
    def extensions(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "extensions"))

    @extensions.setter
    def extensions(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67054a88f0195f702780f758fb7c01f29cd4ca43946a2643fe40fe5c14dadac6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "extensions", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad38f9644005ade28aa84d1266e427f63903eb8732e7623adf4a803c67933d9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53fc7b3475d57effccc6da2ce2551be80fb2965f170631f0d4d548633a502053)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="principals")
    def principals(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principals"))

    @principals.setter
    def principals(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__417ea6d6fb14a279cfea513ec65e973e9f75ef7a80961d42fa9231ec20ebf110)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "principals", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionApi")
    def secure_access_bastion_api(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionApi"))

    @secure_access_bastion_api.setter
    def secure_access_bastion_api(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__613aea66039129c2a2daae6c88afab590e02cce71bc1773d55bb52f443a509a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionApi", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionSsh")
    def secure_access_bastion_ssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionSsh"))

    @secure_access_bastion_ssh.setter
    def secure_access_bastion_ssh(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__807a5f4f9f888fdeca194159505846e0f94641b9674aab596f1b6297b6e5f40b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionSsh", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c653ecad09ed66a584dde0a37eb107367a95d1364d71704fc23b9fa1adacea8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f97bcb4811fbaab79c187f5e63b1a95354e872769f423aac372d27273a71ac9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessHost", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessSshCredsUser")
    def secure_access_ssh_creds_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessSshCredsUser"))

    @secure_access_ssh_creds_user.setter
    def secure_access_ssh_creds_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccd3cf5daab2ac7e7a159059d41c87c78c53091b60eb91874fd7c44f777b7020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessSshCredsUser", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessUseInternalBastion")
    def secure_access_use_internal_bastion(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessUseInternalBastion"))

    @secure_access_use_internal_bastion.setter
    def secure_access_use_internal_bastion(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1b13cffd8c43d5685e7b2d599751540237d411c9acfad720ad681a42171bdbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessUseInternalBastion", value)

    @builtins.property
    @jsii.member(jsii_name="signerKeyName")
    def signer_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signerKeyName"))

    @signer_key_name.setter
    def signer_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbff2f18ad265374db9fc899beb951da99bdaf266c1cd06e8d5ef65bf54060cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signerKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe0dc553eaa8285e960f8188eb02e7ce455134d3605f5127b167e93629f36e71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bf0fbf6ed1c78d81686ae87b948089b68d673c78f425a3a461b71fdb2fae6a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value)


@jsii.data_type(
    jsii_type="akeyless.sshCertIssuer.SshCertIssuerConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "allowed_users": "allowedUsers",
        "name": "name",
        "signer_key_name": "signerKeyName",
        "ttl": "ttl",
        "delete_protection": "deleteProtection",
        "description": "description",
        "extensions": "extensions",
        "id": "id",
        "principals": "principals",
        "secure_access_bastion_api": "secureAccessBastionApi",
        "secure_access_bastion_ssh": "secureAccessBastionSsh",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_host": "secureAccessHost",
        "secure_access_ssh_creds_user": "secureAccessSshCredsUser",
        "secure_access_use_internal_bastion": "secureAccessUseInternalBastion",
        "tags": "tags",
    },
)
class SshCertIssuerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        allowed_users: builtins.str,
        name: builtins.str,
        signer_key_name: builtins.str,
        ttl: jsii.Number,
        delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        description: typing.Optional[builtins.str] = None,
        extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        principals: typing.Optional[builtins.str] = None,
        secure_access_bastion_api: typing.Optional[builtins.str] = None,
        secure_access_bastion_ssh: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_ssh_creds_user: typing.Optional[builtins.str] = None,
        secure_access_use_internal_bastion: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param allowed_users: Users allowed to fetch the certificate, e.g root,ubuntu. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#allowed_users SshCertIssuer#allowed_users}
        :param name: SSH certificate issuer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#name SshCertIssuer#name}
        :param signer_key_name: A key to sign the certificate with. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#signer_key_name SshCertIssuer#signer_key_name}
        :param ttl: The requested Time To Live for the certificate, in seconds. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#ttl SshCertIssuer#ttl}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#delete_protection SshCertIssuer#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#description SshCertIssuer#description}
        :param extensions: Signed certificates with extensions (key/val), e.g permit-port-forwarding=. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#extensions SshCertIssuer#extensions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#id SshCertIssuer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param principals: Signed certificates with principal, e.g example_role1,example_role2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#principals SshCertIssuer#principals}
        :param secure_access_bastion_api: Bastion's SSH control API endpoint. E.g. https://my.bastion:9900. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_bastion_api SshCertIssuer#secure_access_bastion_api}
        :param secure_access_bastion_ssh: Bastion's SSH server. E.g. my.bastion:22. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_bastion_ssh SshCertIssuer#secure_access_bastion_ssh}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_enable SshCertIssuer#secure_access_enable}
        :param secure_access_host: Target servers for connections. (In case of Linked Target association, host(s) will inherit Linked Target hosts - Relevant only for Dynamic Secrets/producers) Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_host SshCertIssuer#secure_access_host}
        :param secure_access_ssh_creds_user: SSH username to connect to target server, must be in 'Allowed Users' list. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_ssh_creds_user SshCertIssuer#secure_access_ssh_creds_user}
        :param secure_access_use_internal_bastion: Use internal SSH Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_use_internal_bastion SshCertIssuer#secure_access_use_internal_bastion}
        :param tags: List of the tags attached to this key. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#tags SshCertIssuer#tags}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a570ebd57e4703d29a63441f76bea8516ce928751b3a434f5676e19e179e721c)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument allowed_users", value=allowed_users, expected_type=type_hints["allowed_users"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument signer_key_name", value=signer_key_name, expected_type=type_hints["signer_key_name"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument extensions", value=extensions, expected_type=type_hints["extensions"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument principals", value=principals, expected_type=type_hints["principals"])
            check_type(argname="argument secure_access_bastion_api", value=secure_access_bastion_api, expected_type=type_hints["secure_access_bastion_api"])
            check_type(argname="argument secure_access_bastion_ssh", value=secure_access_bastion_ssh, expected_type=type_hints["secure_access_bastion_ssh"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_host", value=secure_access_host, expected_type=type_hints["secure_access_host"])
            check_type(argname="argument secure_access_ssh_creds_user", value=secure_access_ssh_creds_user, expected_type=type_hints["secure_access_ssh_creds_user"])
            check_type(argname="argument secure_access_use_internal_bastion", value=secure_access_use_internal_bastion, expected_type=type_hints["secure_access_use_internal_bastion"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "allowed_users": allowed_users,
            "name": name,
            "signer_key_name": signer_key_name,
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
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if extensions is not None:
            self._values["extensions"] = extensions
        if id is not None:
            self._values["id"] = id
        if principals is not None:
            self._values["principals"] = principals
        if secure_access_bastion_api is not None:
            self._values["secure_access_bastion_api"] = secure_access_bastion_api
        if secure_access_bastion_ssh is not None:
            self._values["secure_access_bastion_ssh"] = secure_access_bastion_ssh
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_host is not None:
            self._values["secure_access_host"] = secure_access_host
        if secure_access_ssh_creds_user is not None:
            self._values["secure_access_ssh_creds_user"] = secure_access_ssh_creds_user
        if secure_access_use_internal_bastion is not None:
            self._values["secure_access_use_internal_bastion"] = secure_access_use_internal_bastion
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
    def allowed_users(self) -> builtins.str:
        '''Users allowed to fetch the certificate, e.g root,ubuntu.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#allowed_users SshCertIssuer#allowed_users}
        '''
        result = self._values.get("allowed_users")
        assert result is not None, "Required property 'allowed_users' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''SSH certificate issuer name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#name SshCertIssuer#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def signer_key_name(self) -> builtins.str:
        '''A key to sign the certificate with.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#signer_key_name SshCertIssuer#signer_key_name}
        '''
        result = self._values.get("signer_key_name")
        assert result is not None, "Required property 'signer_key_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ttl(self) -> jsii.Number:
        '''The requested Time To Live for the certificate, in seconds.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#ttl SshCertIssuer#ttl}
        '''
        result = self._values.get("ttl")
        assert result is not None, "Required property 'ttl' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def delete_protection(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Protection from accidental deletion of this item, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#delete_protection SshCertIssuer#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#description SshCertIssuer#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extensions(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Signed certificates with extensions (key/val), e.g permit-port-forwarding=.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#extensions SshCertIssuer#extensions}
        '''
        result = self._values.get("extensions")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#id SshCertIssuer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def principals(self) -> typing.Optional[builtins.str]:
        '''Signed certificates with principal, e.g example_role1,example_role2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#principals SshCertIssuer#principals}
        '''
        result = self._values.get("principals")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_api(self) -> typing.Optional[builtins.str]:
        '''Bastion's SSH control API endpoint. E.g. https://my.bastion:9900.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_bastion_api SshCertIssuer#secure_access_bastion_api}
        '''
        result = self._values.get("secure_access_bastion_api")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_ssh(self) -> typing.Optional[builtins.str]:
        '''Bastion's SSH server. E.g. my.bastion:22.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_bastion_ssh SshCertIssuer#secure_access_bastion_ssh}
        '''
        result = self._values.get("secure_access_bastion_ssh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_enable SshCertIssuer#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target servers for connections.

        (In case of Linked Target association, host(s) will inherit Linked Target hosts - Relevant only for Dynamic Secrets/producers)

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_host SshCertIssuer#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_ssh_creds_user(self) -> typing.Optional[builtins.str]:
        '''SSH username to connect to target server, must be in 'Allowed Users' list.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_ssh_creds_user SshCertIssuer#secure_access_ssh_creds_user}
        '''
        result = self._values.get("secure_access_ssh_creds_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_use_internal_bastion(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use internal SSH Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#secure_access_use_internal_bastion SshCertIssuer#secure_access_use_internal_bastion}
        '''
        result = self._values.get("secure_access_use_internal_bastion")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this key.

        To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/ssh_cert_issuer#tags SshCertIssuer#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SshCertIssuerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "SshCertIssuer",
    "SshCertIssuerConfig",
]

publication.publish()

def _typecheckingstub__2ab6801d9809be063348fa5ab7a1d2c7dc0538767c6da011faba0e813715c878(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    allowed_users: builtins.str,
    name: builtins.str,
    signer_key_name: builtins.str,
    ttl: jsii.Number,
    delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    principals: typing.Optional[builtins.str] = None,
    secure_access_bastion_api: typing.Optional[builtins.str] = None,
    secure_access_bastion_ssh: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_ssh_creds_user: typing.Optional[builtins.str] = None,
    secure_access_use_internal_bastion: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__1a22f09cc76449786e7b9affe402ce4422cf91514ee547c19a753a54863a9aa9(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6dd2e0d3d713739f8683186320045cfc270b18f0f3e6307dffd34f25d1510ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3755bd8c34b294b59c3043515b6ef25e63c713c7eae3245f0d596df7428192d1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36883315a5cb4df62872c21b9782dd51864a228693430c453164e4905f6e7928(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67054a88f0195f702780f758fb7c01f29cd4ca43946a2643fe40fe5c14dadac6(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad38f9644005ade28aa84d1266e427f63903eb8732e7623adf4a803c67933d9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53fc7b3475d57effccc6da2ce2551be80fb2965f170631f0d4d548633a502053(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__417ea6d6fb14a279cfea513ec65e973e9f75ef7a80961d42fa9231ec20ebf110(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__613aea66039129c2a2daae6c88afab590e02cce71bc1773d55bb52f443a509a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__807a5f4f9f888fdeca194159505846e0f94641b9674aab596f1b6297b6e5f40b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c653ecad09ed66a584dde0a37eb107367a95d1364d71704fc23b9fa1adacea8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f97bcb4811fbaab79c187f5e63b1a95354e872769f423aac372d27273a71ac9(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccd3cf5daab2ac7e7a159059d41c87c78c53091b60eb91874fd7c44f777b7020(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1b13cffd8c43d5685e7b2d599751540237d411c9acfad720ad681a42171bdbb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbff2f18ad265374db9fc899beb951da99bdaf266c1cd06e8d5ef65bf54060cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe0dc553eaa8285e960f8188eb02e7ce455134d3605f5127b167e93629f36e71(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bf0fbf6ed1c78d81686ae87b948089b68d673c78f425a3a461b71fdb2fae6a7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a570ebd57e4703d29a63441f76bea8516ce928751b3a434f5676e19e179e721c(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    allowed_users: builtins.str,
    name: builtins.str,
    signer_key_name: builtins.str,
    ttl: jsii.Number,
    delete_protection: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    description: typing.Optional[builtins.str] = None,
    extensions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    principals: typing.Optional[builtins.str] = None,
    secure_access_bastion_api: typing.Optional[builtins.str] = None,
    secure_access_bastion_ssh: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_ssh_creds_user: typing.Optional[builtins.str] = None,
    secure_access_use_internal_bastion: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
