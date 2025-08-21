'''
# `akeyless_static_secret`

Refer to the Terraform Registry for docs: [`akeyless_static_secret`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret).
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


class StaticSecret(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.staticSecret.StaticSecret",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret akeyless_static_secret}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        path: builtins.str,
        custom_field: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        inject_url: typing.Optional[typing.Sequence[builtins.str]] = None,
        keep_prev_version: typing.Optional[builtins.str] = None,
        multiline_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        password: typing.Optional[builtins.str] = None,
        protection_key: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_ssh_creds: typing.Optional[builtins.str] = None,
        secure_access_ssh_user: typing.Optional[builtins.str] = None,
        secure_access_url: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret akeyless_static_secret} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param path: The path where the secret will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#path StaticSecret#path}
        :param custom_field: Additional custom fields to associate with the item (e.g fieldName1=value1) (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#custom_field StaticSecret#custom_field}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#delete_protection StaticSecret#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#description StaticSecret#description}
        :param format: Secret format [text/json/key-value] (relevant only for type 'generic'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#format StaticSecret#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#id StaticSecret#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param inject_url: List of URLs associated with the item (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#inject_url StaticSecret#inject_url}
        :param keep_prev_version: Whether to keep previous version [true/false]. If not set, use default according to account settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#keep_prev_version StaticSecret#keep_prev_version}
        :param multiline_value: The provided value is a multiline value (separated by ' '). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#multiline_value StaticSecret#multiline_value}
        :param password: Password value (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#password StaticSecret#password}
        :param protection_key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#protection_key StaticSecret#protection_key}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Secure Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_bastion_issuer StaticSecret#secure_access_bastion_issuer}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_enable StaticSecret#secure_access_enable}
        :param secure_access_host: Target servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_host StaticSecret#secure_access_host}
        :param secure_access_ssh_creds: Static-Secret values contains SSH Credentials, either Private Key or Password [password/private-key]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_ssh_creds StaticSecret#secure_access_ssh_creds}
        :param secure_access_ssh_user: Override the SSH username as indicated in SSH Certificate Issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_ssh_user StaticSecret#secure_access_ssh_user}
        :param secure_access_url: Destination URL to inject secrets. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_url StaticSecret#secure_access_url}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_web StaticSecret#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless's Secure Remote Access (SRA). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_web_browsing StaticSecret#secure_access_web_browsing}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#tags StaticSecret#tags}
        :param type: Secret type [generic/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#type StaticSecret#type}
        :param username: Username value (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#username StaticSecret#username}
        :param value: The secret content. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#value StaticSecret#value}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b8936f20c198668290e0c22515e857576f931b75a56fe96ec9821a84710b34e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = StaticSecretConfig(
            path=path,
            custom_field=custom_field,
            delete_protection=delete_protection,
            description=description,
            format=format,
            id=id,
            inject_url=inject_url,
            keep_prev_version=keep_prev_version,
            multiline_value=multiline_value,
            password=password,
            protection_key=protection_key,
            secure_access_bastion_issuer=secure_access_bastion_issuer,
            secure_access_enable=secure_access_enable,
            secure_access_host=secure_access_host,
            secure_access_ssh_creds=secure_access_ssh_creds,
            secure_access_ssh_user=secure_access_ssh_user,
            secure_access_url=secure_access_url,
            secure_access_web=secure_access_web,
            secure_access_web_browsing=secure_access_web_browsing,
            tags=tags,
            type=type,
            username=username,
            value=value,
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
        '''Generates CDKTF code for importing a StaticSecret resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the StaticSecret to import.
        :param import_from_id: The id of the existing StaticSecret that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the StaticSecret to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__657618c0e9067007d1b9502615467d1f59166344b68b1b2f0c6e539c38009c25)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomField")
    def reset_custom_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomField", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFormat")
    def reset_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFormat", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInjectUrl")
    def reset_inject_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInjectUrl", []))

    @jsii.member(jsii_name="resetKeepPrevVersion")
    def reset_keep_prev_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepPrevVersion", []))

    @jsii.member(jsii_name="resetMultilineValue")
    def reset_multiline_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMultilineValue", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetProtectionKey")
    def reset_protection_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtectionKey", []))

    @jsii.member(jsii_name="resetSecureAccessBastionIssuer")
    def reset_secure_access_bastion_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessBastionIssuer", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

    @jsii.member(jsii_name="resetSecureAccessHost")
    def reset_secure_access_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessHost", []))

    @jsii.member(jsii_name="resetSecureAccessSshCreds")
    def reset_secure_access_ssh_creds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessSshCreds", []))

    @jsii.member(jsii_name="resetSecureAccessSshUser")
    def reset_secure_access_ssh_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessSshUser", []))

    @jsii.member(jsii_name="resetSecureAccessUrl")
    def reset_secure_access_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessUrl", []))

    @jsii.member(jsii_name="resetSecureAccessWeb")
    def reset_secure_access_web(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWeb", []))

    @jsii.member(jsii_name="resetSecureAccessWebBrowsing")
    def reset_secure_access_web_browsing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWebBrowsing", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

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
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="customFieldInput")
    def custom_field_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "customFieldInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="formatInput")
    def format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "formatInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="injectUrlInput")
    def inject_url_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "injectUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="keepPrevVersionInput")
    def keep_prev_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keepPrevVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="multilineValueInput")
    def multiline_value_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "multilineValueInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="protectionKeyInput")
    def protection_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protectionKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuerInput")
    def secure_access_bastion_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessBastionIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessHostInput")
    def secure_access_host_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "secureAccessHostInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessSshCredsInput")
    def secure_access_ssh_creds_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessSshCredsInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessSshUserInput")
    def secure_access_ssh_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessSshUserInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessUrlInput")
    def secure_access_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessWebBrowsingInput")
    def secure_access_web_browsing_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessWebBrowsingInput"))

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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="customField")
    def custom_field(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "customField"))

    @custom_field.setter
    def custom_field(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33c17e8b876541170f07c5d707451f1b7cfd05a2b2685be697aabd15dc65de92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customField", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0b6c2977c612214b5fb661c3ebc1f8eadf7d813c45225bae6fa4d9cc66d0761)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3903c7ed0cd67e9c02b8d336767ecf00245d6c37db54f1d02d7c51f5b19eafb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="format")
    def format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "format"))

    @format.setter
    def format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a42e6a3e608ebf878ae188fe3d8e881006bf623893858a4e5914a80326d51b38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "format", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__937c46c1e0c7fc3b9fb4ea54895182e2ea949b8fb09c5a031bd0096c404b26a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="injectUrl")
    def inject_url(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "injectUrl"))

    @inject_url.setter
    def inject_url(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be9efbf5eefb9fccdb006fbaeb1f28c5685d423809b0cfc360b43770fd581aeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "injectUrl", value)

    @builtins.property
    @jsii.member(jsii_name="keepPrevVersion")
    def keep_prev_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keepPrevVersion"))

    @keep_prev_version.setter
    def keep_prev_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9071532ba3d160324339858ca474934542733603699bc3812dd4bc6a0dbcdc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keepPrevVersion", value)

    @builtins.property
    @jsii.member(jsii_name="multilineValue")
    def multiline_value(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "multilineValue"))

    @multiline_value.setter
    def multiline_value(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bafa121233c156545279895aa88d6cb7ae132ed492bed24e60c103bfefdebe6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "multilineValue", value)

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84f8c72996e1a493ec048fa884231b9759101faad24d2937a4d1419df9203427)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value)

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6e3e5edf3dcd86fc030f9f2143a65db9973a7c92a48f40bbc15530504bbc3a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)

    @builtins.property
    @jsii.member(jsii_name="protectionKey")
    def protection_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protectionKey"))

    @protection_key.setter
    def protection_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1cdf2b5d9146f2e4382b214539e0e296403513d3c05ce8aec659a7c4047824f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protectionKey", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a02b3b68b2607287be9aadee5b93be744a310889f3161f830cca0ae1b5855f58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04baf2f67c3d0ecfde099be720f6a8a8fb1ffd57d51fbe557c07f3f7eb7ef7ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6aa99aa0a8b39fb420eba7ffc6d935d097cd998095cf2e13dee7c042afe66f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessHost", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessSshCreds")
    def secure_access_ssh_creds(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessSshCreds"))

    @secure_access_ssh_creds.setter
    def secure_access_ssh_creds(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1ae11c88d8c1e739b357154e8617ef772e575f6638a501ebb61963e28dcc8c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessSshCreds", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessSshUser")
    def secure_access_ssh_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessSshUser"))

    @secure_access_ssh_user.setter
    def secure_access_ssh_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5df202881ba88c806ea4001e619194661a8df62566cf3d947ab9e8e8d11e93b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessSshUser", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessUrl")
    def secure_access_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessUrl"))

    @secure_access_url.setter
    def secure_access_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1659bc733ae022022fdc9d39820eca5f9a600efe6302e2a1dfdbe2378291328)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessUrl", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__43c548df30d5139f6fad1b83a6f73d3ebff3c36522a7aa1c042915aaa3c75fbb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessWebBrowsing")
    def secure_access_web_browsing(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessWebBrowsing"))

    @secure_access_web_browsing.setter
    def secure_access_web_browsing(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__886afd64fe0c38107ffff19bd8fefd9eb63301d82d57ab09589c4ad868059a0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWebBrowsing", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17c44d9a8e15993561ab5186a59e66185328e2cd1b27ae57b4da1c90f6e0524f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__578e2520df4c0be99de6d743f1b99c2d6ab2a656853e56eac408c7c25a355d31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b85195c6adbbce08a7726663eed3c0f6368c611929309c27f62ed6445cf1876)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value)

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b72d04db3db55a73e36c7147bcb1529fd0a05844218697a28225c64756c12c20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value)


@jsii.data_type(
    jsii_type="akeyless.staticSecret.StaticSecretConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "path": "path",
        "custom_field": "customField",
        "delete_protection": "deleteProtection",
        "description": "description",
        "format": "format",
        "id": "id",
        "inject_url": "injectUrl",
        "keep_prev_version": "keepPrevVersion",
        "multiline_value": "multilineValue",
        "password": "password",
        "protection_key": "protectionKey",
        "secure_access_bastion_issuer": "secureAccessBastionIssuer",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_host": "secureAccessHost",
        "secure_access_ssh_creds": "secureAccessSshCreds",
        "secure_access_ssh_user": "secureAccessSshUser",
        "secure_access_url": "secureAccessUrl",
        "secure_access_web": "secureAccessWeb",
        "secure_access_web_browsing": "secureAccessWebBrowsing",
        "tags": "tags",
        "type": "type",
        "username": "username",
        "value": "value",
    },
)
class StaticSecretConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        path: builtins.str,
        custom_field: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        format: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        inject_url: typing.Optional[typing.Sequence[builtins.str]] = None,
        keep_prev_version: typing.Optional[builtins.str] = None,
        multiline_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        password: typing.Optional[builtins.str] = None,
        protection_key: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
        secure_access_ssh_creds: typing.Optional[builtins.str] = None,
        secure_access_ssh_user: typing.Optional[builtins.str] = None,
        secure_access_url: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param path: The path where the secret will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#path StaticSecret#path}
        :param custom_field: Additional custom fields to associate with the item (e.g fieldName1=value1) (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#custom_field StaticSecret#custom_field}
        :param delete_protection: Protection from accidental deletion of this auth method, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#delete_protection StaticSecret#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#description StaticSecret#description}
        :param format: Secret format [text/json/key-value] (relevant only for type 'generic'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#format StaticSecret#format}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#id StaticSecret#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param inject_url: List of URLs associated with the item (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#inject_url StaticSecret#inject_url}
        :param keep_prev_version: Whether to keep previous version [true/false]. If not set, use default according to account settings. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#keep_prev_version StaticSecret#keep_prev_version}
        :param multiline_value: The provided value is a multiline value (separated by ' '). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#multiline_value StaticSecret#multiline_value}
        :param password: Password value (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#password StaticSecret#password}
        :param protection_key: The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#protection_key StaticSecret#protection_key}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Secure Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_bastion_issuer StaticSecret#secure_access_bastion_issuer}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_enable StaticSecret#secure_access_enable}
        :param secure_access_host: Target servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_host StaticSecret#secure_access_host}
        :param secure_access_ssh_creds: Static-Secret values contains SSH Credentials, either Private Key or Password [password/private-key]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_ssh_creds StaticSecret#secure_access_ssh_creds}
        :param secure_access_ssh_user: Override the SSH username as indicated in SSH Certificate Issuer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_ssh_user StaticSecret#secure_access_ssh_user}
        :param secure_access_url: Destination URL to inject secrets. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_url StaticSecret#secure_access_url}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_web StaticSecret#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless's Secure Remote Access (SRA). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_web_browsing StaticSecret#secure_access_web_browsing}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#tags StaticSecret#tags}
        :param type: Secret type [generic/password]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#type StaticSecret#type}
        :param username: Username value (relevant only for type 'password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#username StaticSecret#username}
        :param value: The secret content. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#value StaticSecret#value}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c61bd0814a263ee2011bbf7992f06a9f70bc08808c3f7e4daed259458375a0f3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument custom_field", value=custom_field, expected_type=type_hints["custom_field"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument format", value=format, expected_type=type_hints["format"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument inject_url", value=inject_url, expected_type=type_hints["inject_url"])
            check_type(argname="argument keep_prev_version", value=keep_prev_version, expected_type=type_hints["keep_prev_version"])
            check_type(argname="argument multiline_value", value=multiline_value, expected_type=type_hints["multiline_value"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument protection_key", value=protection_key, expected_type=type_hints["protection_key"])
            check_type(argname="argument secure_access_bastion_issuer", value=secure_access_bastion_issuer, expected_type=type_hints["secure_access_bastion_issuer"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_host", value=secure_access_host, expected_type=type_hints["secure_access_host"])
            check_type(argname="argument secure_access_ssh_creds", value=secure_access_ssh_creds, expected_type=type_hints["secure_access_ssh_creds"])
            check_type(argname="argument secure_access_ssh_user", value=secure_access_ssh_user, expected_type=type_hints["secure_access_ssh_user"])
            check_type(argname="argument secure_access_url", value=secure_access_url, expected_type=type_hints["secure_access_url"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
            check_type(argname="argument secure_access_web_browsing", value=secure_access_web_browsing, expected_type=type_hints["secure_access_web_browsing"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "path": path,
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
        if custom_field is not None:
            self._values["custom_field"] = custom_field
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if format is not None:
            self._values["format"] = format
        if id is not None:
            self._values["id"] = id
        if inject_url is not None:
            self._values["inject_url"] = inject_url
        if keep_prev_version is not None:
            self._values["keep_prev_version"] = keep_prev_version
        if multiline_value is not None:
            self._values["multiline_value"] = multiline_value
        if password is not None:
            self._values["password"] = password
        if protection_key is not None:
            self._values["protection_key"] = protection_key
        if secure_access_bastion_issuer is not None:
            self._values["secure_access_bastion_issuer"] = secure_access_bastion_issuer
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_host is not None:
            self._values["secure_access_host"] = secure_access_host
        if secure_access_ssh_creds is not None:
            self._values["secure_access_ssh_creds"] = secure_access_ssh_creds
        if secure_access_ssh_user is not None:
            self._values["secure_access_ssh_user"] = secure_access_ssh_user
        if secure_access_url is not None:
            self._values["secure_access_url"] = secure_access_url
        if secure_access_web is not None:
            self._values["secure_access_web"] = secure_access_web
        if secure_access_web_browsing is not None:
            self._values["secure_access_web_browsing"] = secure_access_web_browsing
        if tags is not None:
            self._values["tags"] = tags
        if type is not None:
            self._values["type"] = type
        if username is not None:
            self._values["username"] = username
        if value is not None:
            self._values["value"] = value

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
    def path(self) -> builtins.str:
        '''The path where the secret will be stored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#path StaticSecret#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_field(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional custom fields to associate with the item (e.g fieldName1=value1) (relevant only for type 'password').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#custom_field StaticSecret#custom_field}
        '''
        result = self._values.get("custom_field")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this auth method, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#delete_protection StaticSecret#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#description StaticSecret#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def format(self) -> typing.Optional[builtins.str]:
        '''Secret format [text/json/key-value] (relevant only for type 'generic').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#format StaticSecret#format}
        '''
        result = self._values.get("format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#id StaticSecret#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inject_url(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URLs associated with the item (relevant only for type 'password').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#inject_url StaticSecret#inject_url}
        '''
        result = self._values.get("inject_url")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def keep_prev_version(self) -> typing.Optional[builtins.str]:
        '''Whether to keep previous version [true/false]. If not set, use default according to account settings.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#keep_prev_version StaticSecret#keep_prev_version}
        '''
        result = self._values.get("keep_prev_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def multiline_value(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The provided value is a multiline value (separated by ' ').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#multiline_value StaticSecret#multiline_value}
        '''
        result = self._values.get("multiline_value")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password value (relevant only for type 'password').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#password StaticSecret#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protection_key(self) -> typing.Optional[builtins.str]:
        '''The name of a key that is used to encrypt the secret value (if empty, the account default protectionKey key will be used).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#protection_key StaticSecret#protection_key}
        '''
        result = self._values.get("protection_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Secure Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_bastion_issuer StaticSecret#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_enable StaticSecret#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target servers for connections., For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_host StaticSecret#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_ssh_creds(self) -> typing.Optional[builtins.str]:
        '''Static-Secret values contains SSH Credentials, either Private Key or Password [password/private-key].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_ssh_creds StaticSecret#secure_access_ssh_creds}
        '''
        result = self._values.get("secure_access_ssh_creds")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_ssh_user(self) -> typing.Optional[builtins.str]:
        '''Override the SSH username as indicated in SSH Certificate Issuer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_ssh_user StaticSecret#secure_access_ssh_user}
        '''
        result = self._values.get("secure_access_ssh_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_url(self) -> typing.Optional[builtins.str]:
        '''Destination URL to inject secrets.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_url StaticSecret#secure_access_url}
        '''
        result = self._values.get("secure_access_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_web StaticSecret#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_web_browsing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Secure browser via Akeyless's Secure Remote Access (SRA).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#secure_access_web_browsing StaticSecret#secure_access_web_browsing}
        '''
        result = self._values.get("secure_access_web_browsing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#tags StaticSecret#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Secret type [generic/password].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#type StaticSecret#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Username value (relevant only for type 'password').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#username StaticSecret#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''The secret content.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/static_secret#value StaticSecret#value}
        '''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticSecretConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "StaticSecret",
    "StaticSecretConfig",
]

publication.publish()

def _typecheckingstub__6b8936f20c198668290e0c22515e857576f931b75a56fe96ec9821a84710b34e(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    path: builtins.str,
    custom_field: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    inject_url: typing.Optional[typing.Sequence[builtins.str]] = None,
    keep_prev_version: typing.Optional[builtins.str] = None,
    multiline_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    password: typing.Optional[builtins.str] = None,
    protection_key: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_ssh_creds: typing.Optional[builtins.str] = None,
    secure_access_ssh_user: typing.Optional[builtins.str] = None,
    secure_access_url: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__657618c0e9067007d1b9502615467d1f59166344b68b1b2f0c6e539c38009c25(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33c17e8b876541170f07c5d707451f1b7cfd05a2b2685be697aabd15dc65de92(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0b6c2977c612214b5fb661c3ebc1f8eadf7d813c45225bae6fa4d9cc66d0761(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3903c7ed0cd67e9c02b8d336767ecf00245d6c37db54f1d02d7c51f5b19eafb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a42e6a3e608ebf878ae188fe3d8e881006bf623893858a4e5914a80326d51b38(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__937c46c1e0c7fc3b9fb4ea54895182e2ea949b8fb09c5a031bd0096c404b26a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be9efbf5eefb9fccdb006fbaeb1f28c5685d423809b0cfc360b43770fd581aeb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9071532ba3d160324339858ca474934542733603699bc3812dd4bc6a0dbcdc4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bafa121233c156545279895aa88d6cb7ae132ed492bed24e60c103bfefdebe6f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84f8c72996e1a493ec048fa884231b9759101faad24d2937a4d1419df9203427(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6e3e5edf3dcd86fc030f9f2143a65db9973a7c92a48f40bbc15530504bbc3a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1cdf2b5d9146f2e4382b214539e0e296403513d3c05ce8aec659a7c4047824f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a02b3b68b2607287be9aadee5b93be744a310889f3161f830cca0ae1b5855f58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04baf2f67c3d0ecfde099be720f6a8a8fb1ffd57d51fbe557c07f3f7eb7ef7ae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6aa99aa0a8b39fb420eba7ffc6d935d097cd998095cf2e13dee7c042afe66f6(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1ae11c88d8c1e739b357154e8617ef772e575f6638a501ebb61963e28dcc8c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5df202881ba88c806ea4001e619194661a8df62566cf3d947ab9e8e8d11e93b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1659bc733ae022022fdc9d39820eca5f9a600efe6302e2a1dfdbe2378291328(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43c548df30d5139f6fad1b83a6f73d3ebff3c36522a7aa1c042915aaa3c75fbb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__886afd64fe0c38107ffff19bd8fefd9eb63301d82d57ab09589c4ad868059a0e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17c44d9a8e15993561ab5186a59e66185328e2cd1b27ae57b4da1c90f6e0524f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__578e2520df4c0be99de6d743f1b99c2d6ab2a656853e56eac408c7c25a355d31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b85195c6adbbce08a7726663eed3c0f6368c611929309c27f62ed6445cf1876(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b72d04db3db55a73e36c7147bcb1529fd0a05844218697a28225c64756c12c20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61bd0814a263ee2011bbf7992f06a9f70bc08808c3f7e4daed259458375a0f3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    path: builtins.str,
    custom_field: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    format: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    inject_url: typing.Optional[typing.Sequence[builtins.str]] = None,
    keep_prev_version: typing.Optional[builtins.str] = None,
    multiline_value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    password: typing.Optional[builtins.str] = None,
    protection_key: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_ssh_creds: typing.Optional[builtins.str] = None,
    secure_access_ssh_user: typing.Optional[builtins.str] = None,
    secure_access_url: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    type: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
