'''
# `akeyless_dynamic_secret_azure`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_azure`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure).
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


class DynamicSecretAzure(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretAzure.DynamicSecretAzure",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure akeyless_dynamic_secret_azure}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        app_obj_id: typing.Optional[builtins.str] = None,
        azure_client_id: typing.Optional[builtins.str] = None,
        azure_client_secret: typing.Optional[builtins.str] = None,
        azure_tenant_id: typing.Optional[builtins.str] = None,
        custom_username_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_url: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        user_group_obj_id: typing.Optional[builtins.str] = None,
        user_portal_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user_principal_name: typing.Optional[builtins.str] = None,
        user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user_role_template_id: typing.Optional[builtins.str] = None,
        user_ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure akeyless_dynamic_secret_azure} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#name DynamicSecretAzure#name}
        :param app_obj_id: Azure App Object ID (required if selected programmatic access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#app_obj_id DynamicSecretAzure#app_obj_id}
        :param azure_client_id: Azure Client ID (Application ID). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_client_id DynamicSecretAzure#azure_client_id}
        :param azure_client_secret: Azure AD Client Secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_client_secret DynamicSecretAzure#azure_client_secret}
        :param azure_tenant_id: Azure Tenant ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_tenant_id DynamicSecretAzure#azure_tenant_id}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#custom_username_template DynamicSecretAzure#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#encryption_key_name DynamicSecretAzure#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#id DynamicSecretAzure#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#password_length DynamicSecretAzure#password_length}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_enable DynamicSecretAzure#secure_access_enable}
        :param secure_access_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_url DynamicSecretAzure#secure_access_url}.
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_web DynamicSecretAzure#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_web_browsing DynamicSecretAzure#secure_access_web_browsing}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#tags DynamicSecretAzure#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#target_name DynamicSecretAzure#target_name}
        :param user_group_obj_id: Azure AD User Group Object ID (required if selected Portal access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_group_obj_id DynamicSecretAzure#user_group_obj_id}
        :param user_portal_access: Enable Azure AD user portal access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_portal_access DynamicSecretAzure#user_portal_access}
        :param user_principal_name: Azure AD User Principal Name (required if selected Portal access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_principal_name DynamicSecretAzure#user_principal_name}
        :param user_programmatic_access: Enable Azure AD user programmatic access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_programmatic_access DynamicSecretAzure#user_programmatic_access}
        :param user_role_template_id: Azure AD User Role Template ID (required if selected Portal access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_role_template_id DynamicSecretAzure#user_role_template_id}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_ttl DynamicSecretAzure#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f803fc002dfd10094dbf7371b54d9989409963f27e076b317d8409bdee4692a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretAzureConfig(
            name=name,
            app_obj_id=app_obj_id,
            azure_client_id=azure_client_id,
            azure_client_secret=azure_client_secret,
            azure_tenant_id=azure_tenant_id,
            custom_username_template=custom_username_template,
            encryption_key_name=encryption_key_name,
            id=id,
            password_length=password_length,
            secure_access_enable=secure_access_enable,
            secure_access_url=secure_access_url,
            secure_access_web=secure_access_web,
            secure_access_web_browsing=secure_access_web_browsing,
            tags=tags,
            target_name=target_name,
            user_group_obj_id=user_group_obj_id,
            user_portal_access=user_portal_access,
            user_principal_name=user_principal_name,
            user_programmatic_access=user_programmatic_access,
            user_role_template_id=user_role_template_id,
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
        '''Generates CDKTF code for importing a DynamicSecretAzure resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretAzure to import.
        :param import_from_id: The id of the existing DynamicSecretAzure that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretAzure to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f04f2212f8aa4e76a66f3c23b04a83a693bc29b428ece3a4db6a9a9b850a4e67)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAppObjId")
    def reset_app_obj_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppObjId", []))

    @jsii.member(jsii_name="resetAzureClientId")
    def reset_azure_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureClientId", []))

    @jsii.member(jsii_name="resetAzureClientSecret")
    def reset_azure_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureClientSecret", []))

    @jsii.member(jsii_name="resetAzureTenantId")
    def reset_azure_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureTenantId", []))

    @jsii.member(jsii_name="resetCustomUsernameTemplate")
    def reset_custom_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUsernameTemplate", []))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPasswordLength")
    def reset_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLength", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

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

    @jsii.member(jsii_name="resetTargetName")
    def reset_target_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetName", []))

    @jsii.member(jsii_name="resetUserGroupObjId")
    def reset_user_group_obj_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserGroupObjId", []))

    @jsii.member(jsii_name="resetUserPortalAccess")
    def reset_user_portal_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserPortalAccess", []))

    @jsii.member(jsii_name="resetUserPrincipalName")
    def reset_user_principal_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserPrincipalName", []))

    @jsii.member(jsii_name="resetUserProgrammaticAccess")
    def reset_user_programmatic_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserProgrammaticAccess", []))

    @jsii.member(jsii_name="resetUserRoleTemplateId")
    def reset_user_role_template_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserRoleTemplateId", []))

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
    @jsii.member(jsii_name="appObjIdInput")
    def app_obj_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appObjIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureClientIdInput")
    def azure_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureClientSecretInput")
    def azure_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="azureTenantIdInput")
    def azure_tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureTenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customUsernameTemplateInput")
    def custom_username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customUsernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyNameInput")
    def encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordLengthInput")
    def password_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordLengthInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

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
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userGroupObjIdInput")
    def user_group_obj_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userGroupObjIdInput"))

    @builtins.property
    @jsii.member(jsii_name="userPortalAccessInput")
    def user_portal_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "userPortalAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="userPrincipalNameInput")
    def user_principal_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userPrincipalNameInput"))

    @builtins.property
    @jsii.member(jsii_name="userProgrammaticAccessInput")
    def user_programmatic_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "userProgrammaticAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="userRoleTemplateIdInput")
    def user_role_template_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userRoleTemplateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="userTtlInput")
    def user_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="appObjId")
    def app_obj_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appObjId"))

    @app_obj_id.setter
    def app_obj_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b78b987f98c6ed1349786e9cdc812624d337201b65d7739444c33c13b5f3f64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appObjId", value)

    @builtins.property
    @jsii.member(jsii_name="azureClientId")
    def azure_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureClientId"))

    @azure_client_id.setter
    def azure_client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0de571d94ad2e7148a5b93c9e16091903f3ef3326cda3ce4891877678b5ecd19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureClientId", value)

    @builtins.property
    @jsii.member(jsii_name="azureClientSecret")
    def azure_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureClientSecret"))

    @azure_client_secret.setter
    def azure_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5489195aa38c5b9a770bf01a22516f1979f5e304f47931b9db8e98d245484a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureClientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="azureTenantId")
    def azure_tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureTenantId"))

    @azure_tenant_id.setter
    def azure_tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d1bc981e0640136dfd01deaa1ab60810ccab6cc4b7524b664a8c84438a1ceac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureTenantId", value)

    @builtins.property
    @jsii.member(jsii_name="customUsernameTemplate")
    def custom_username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customUsernameTemplate"))

    @custom_username_template.setter
    def custom_username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__743473c415fe4d8c0a9230bb6a45f656ba8c79203564f67f4f54186ec91876b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customUsernameTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a60522856bb8de8366582b1aa00fac2673b36f981fb68df8c985f07c7b5bac15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cf943c792bc597f9fba51e37e7e9bdfa19c878353187e4154b393ab5d8f60ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4323c9e53c12c2228d8244bbd07f908669183da552cf7af70d578273c321b946)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b8d52652ffc31ace70b31148dd5fa848da3fb96e052ef3b5327997cbba0db48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bfcb568aedcf905228ef18086c7ccd64e210e77d9beec9b461f60cf90b04268)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessUrl")
    def secure_access_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessUrl"))

    @secure_access_url.setter
    def secure_access_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5cd9820ec425d41b16aa77632cc2c62cb6365cbbe8db2381e574a634d961bdc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d0845a309b21b8bcbf0e4b6365ad49b187c06d626ec56361050208538356f9f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b4d4deb12171eccc4b80a76d5e66382b322360088e51461e1f8616943555a80)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWebBrowsing", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e12ef72c15b236f4d3a906ebb5e2657ddd96958c68f453ab1bf6de989b6dd75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cddeff03d5fe2c1b06a0b01d2fbe05ffc0e23d3f5374a67030fc5a776ba7e19c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userGroupObjId")
    def user_group_obj_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userGroupObjId"))

    @user_group_obj_id.setter
    def user_group_obj_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__167665c1ff5fab005a3d5049fc2271c034f2fd88fd08feeb0344fcbecc01d6c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userGroupObjId", value)

    @builtins.property
    @jsii.member(jsii_name="userPortalAccess")
    def user_portal_access(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "userPortalAccess"))

    @user_portal_access.setter
    def user_portal_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__684858e91d7bb0ba93724a980157a807246034173d338f1bb9791b8fd3bdfc19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPortalAccess", value)

    @builtins.property
    @jsii.member(jsii_name="userPrincipalName")
    def user_principal_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userPrincipalName"))

    @user_principal_name.setter
    def user_principal_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aeaa8eca64678023801f190f2526013501a33615795afa9fa64aa6db61100358)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userPrincipalName", value)

    @builtins.property
    @jsii.member(jsii_name="userProgrammaticAccess")
    def user_programmatic_access(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "userProgrammaticAccess"))

    @user_programmatic_access.setter
    def user_programmatic_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41f9a8ffb72bdedbd75bb1a7369fedadb571e061a7b8c6fd6708d32a5e7f3843)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userProgrammaticAccess", value)

    @builtins.property
    @jsii.member(jsii_name="userRoleTemplateId")
    def user_role_template_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userRoleTemplateId"))

    @user_role_template_id.setter
    def user_role_template_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0656c4cbe8e86fe9f6e7d96389c84c70ce2604d66d81bbc014c0435b41b93be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userRoleTemplateId", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2835326285de2b979deebc0d3e1d523774a738add9132b794973aed3db177cb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretAzure.DynamicSecretAzureConfig",
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
        "app_obj_id": "appObjId",
        "azure_client_id": "azureClientId",
        "azure_client_secret": "azureClientSecret",
        "azure_tenant_id": "azureTenantId",
        "custom_username_template": "customUsernameTemplate",
        "encryption_key_name": "encryptionKeyName",
        "id": "id",
        "password_length": "passwordLength",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_url": "secureAccessUrl",
        "secure_access_web": "secureAccessWeb",
        "secure_access_web_browsing": "secureAccessWebBrowsing",
        "tags": "tags",
        "target_name": "targetName",
        "user_group_obj_id": "userGroupObjId",
        "user_portal_access": "userPortalAccess",
        "user_principal_name": "userPrincipalName",
        "user_programmatic_access": "userProgrammaticAccess",
        "user_role_template_id": "userRoleTemplateId",
        "user_ttl": "userTtl",
    },
)
class DynamicSecretAzureConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        app_obj_id: typing.Optional[builtins.str] = None,
        azure_client_id: typing.Optional[builtins.str] = None,
        azure_client_secret: typing.Optional[builtins.str] = None,
        azure_tenant_id: typing.Optional[builtins.str] = None,
        custom_username_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        password_length: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_url: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        user_group_obj_id: typing.Optional[builtins.str] = None,
        user_portal_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user_principal_name: typing.Optional[builtins.str] = None,
        user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        user_role_template_id: typing.Optional[builtins.str] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#name DynamicSecretAzure#name}
        :param app_obj_id: Azure App Object ID (required if selected programmatic access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#app_obj_id DynamicSecretAzure#app_obj_id}
        :param azure_client_id: Azure Client ID (Application ID). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_client_id DynamicSecretAzure#azure_client_id}
        :param azure_client_secret: Azure AD Client Secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_client_secret DynamicSecretAzure#azure_client_secret}
        :param azure_tenant_id: Azure Tenant ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_tenant_id DynamicSecretAzure#azure_tenant_id}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#custom_username_template DynamicSecretAzure#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#encryption_key_name DynamicSecretAzure#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#id DynamicSecretAzure#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#password_length DynamicSecretAzure#password_length}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_enable DynamicSecretAzure#secure_access_enable}
        :param secure_access_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_url DynamicSecretAzure#secure_access_url}.
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_web DynamicSecretAzure#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_web_browsing DynamicSecretAzure#secure_access_web_browsing}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#tags DynamicSecretAzure#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#target_name DynamicSecretAzure#target_name}
        :param user_group_obj_id: Azure AD User Group Object ID (required if selected Portal access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_group_obj_id DynamicSecretAzure#user_group_obj_id}
        :param user_portal_access: Enable Azure AD user portal access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_portal_access DynamicSecretAzure#user_portal_access}
        :param user_principal_name: Azure AD User Principal Name (required if selected Portal access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_principal_name DynamicSecretAzure#user_principal_name}
        :param user_programmatic_access: Enable Azure AD user programmatic access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_programmatic_access DynamicSecretAzure#user_programmatic_access}
        :param user_role_template_id: Azure AD User Role Template ID (required if selected Portal access). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_role_template_id DynamicSecretAzure#user_role_template_id}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_ttl DynamicSecretAzure#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f9bfb445b64398ea3a349915601ed1ccdf094659a30668667411dee5a13cbc)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument app_obj_id", value=app_obj_id, expected_type=type_hints["app_obj_id"])
            check_type(argname="argument azure_client_id", value=azure_client_id, expected_type=type_hints["azure_client_id"])
            check_type(argname="argument azure_client_secret", value=azure_client_secret, expected_type=type_hints["azure_client_secret"])
            check_type(argname="argument azure_tenant_id", value=azure_tenant_id, expected_type=type_hints["azure_tenant_id"])
            check_type(argname="argument custom_username_template", value=custom_username_template, expected_type=type_hints["custom_username_template"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument password_length", value=password_length, expected_type=type_hints["password_length"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_url", value=secure_access_url, expected_type=type_hints["secure_access_url"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
            check_type(argname="argument secure_access_web_browsing", value=secure_access_web_browsing, expected_type=type_hints["secure_access_web_browsing"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument target_name", value=target_name, expected_type=type_hints["target_name"])
            check_type(argname="argument user_group_obj_id", value=user_group_obj_id, expected_type=type_hints["user_group_obj_id"])
            check_type(argname="argument user_portal_access", value=user_portal_access, expected_type=type_hints["user_portal_access"])
            check_type(argname="argument user_principal_name", value=user_principal_name, expected_type=type_hints["user_principal_name"])
            check_type(argname="argument user_programmatic_access", value=user_programmatic_access, expected_type=type_hints["user_programmatic_access"])
            check_type(argname="argument user_role_template_id", value=user_role_template_id, expected_type=type_hints["user_role_template_id"])
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
        if app_obj_id is not None:
            self._values["app_obj_id"] = app_obj_id
        if azure_client_id is not None:
            self._values["azure_client_id"] = azure_client_id
        if azure_client_secret is not None:
            self._values["azure_client_secret"] = azure_client_secret
        if azure_tenant_id is not None:
            self._values["azure_tenant_id"] = azure_tenant_id
        if custom_username_template is not None:
            self._values["custom_username_template"] = custom_username_template
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if id is not None:
            self._values["id"] = id
        if password_length is not None:
            self._values["password_length"] = password_length
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_url is not None:
            self._values["secure_access_url"] = secure_access_url
        if secure_access_web is not None:
            self._values["secure_access_web"] = secure_access_web
        if secure_access_web_browsing is not None:
            self._values["secure_access_web_browsing"] = secure_access_web_browsing
        if tags is not None:
            self._values["tags"] = tags
        if target_name is not None:
            self._values["target_name"] = target_name
        if user_group_obj_id is not None:
            self._values["user_group_obj_id"] = user_group_obj_id
        if user_portal_access is not None:
            self._values["user_portal_access"] = user_portal_access
        if user_principal_name is not None:
            self._values["user_principal_name"] = user_principal_name
        if user_programmatic_access is not None:
            self._values["user_programmatic_access"] = user_programmatic_access
        if user_role_template_id is not None:
            self._values["user_role_template_id"] = user_role_template_id
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
        '''Dynamic secret name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#name DynamicSecretAzure#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_obj_id(self) -> typing.Optional[builtins.str]:
        '''Azure App Object ID (required if selected programmatic access).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#app_obj_id DynamicSecretAzure#app_obj_id}
        '''
        result = self._values.get("app_obj_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_client_id(self) -> typing.Optional[builtins.str]:
        '''Azure Client ID (Application ID).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_client_id DynamicSecretAzure#azure_client_id}
        '''
        result = self._values.get("azure_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_client_secret(self) -> typing.Optional[builtins.str]:
        '''Azure AD Client Secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_client_secret DynamicSecretAzure#azure_client_secret}
        '''
        result = self._values.get("azure_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_tenant_id(self) -> typing.Optional[builtins.str]:
        '''Azure Tenant ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#azure_tenant_id DynamicSecretAzure#azure_tenant_id}
        '''
        result = self._values.get("azure_tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_username_template(self) -> typing.Optional[builtins.str]:
        '''Customize how temporary usernames are generated using go template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#custom_username_template DynamicSecretAzure#custom_username_template}
        '''
        result = self._values.get("custom_username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#encryption_key_name DynamicSecretAzure#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#id DynamicSecretAzure#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#password_length DynamicSecretAzure#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_enable DynamicSecretAzure#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_url DynamicSecretAzure#secure_access_url}.'''
        result = self._values.get("secure_access_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_web DynamicSecretAzure#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_web_browsing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Secure browser via Akeyless Web Access Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#secure_access_web_browsing DynamicSecretAzure#secure_access_web_browsing}
        '''
        result = self._values.get("secure_access_web_browsing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#tags DynamicSecretAzure#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#target_name DynamicSecretAzure#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_group_obj_id(self) -> typing.Optional[builtins.str]:
        '''Azure AD User Group Object ID (required if selected Portal access).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_group_obj_id DynamicSecretAzure#user_group_obj_id}
        '''
        result = self._values.get("user_group_obj_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_portal_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Azure AD user portal access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_portal_access DynamicSecretAzure#user_portal_access}
        '''
        result = self._values.get("user_portal_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def user_principal_name(self) -> typing.Optional[builtins.str]:
        '''Azure AD User Principal Name (required if selected Portal access).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_principal_name DynamicSecretAzure#user_principal_name}
        '''
        result = self._values.get("user_principal_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_programmatic_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Azure AD user programmatic access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_programmatic_access DynamicSecretAzure#user_programmatic_access}
        '''
        result = self._values.get("user_programmatic_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def user_role_template_id(self) -> typing.Optional[builtins.str]:
        '''Azure AD User Role Template ID (required if selected Portal access).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_role_template_id DynamicSecretAzure#user_role_template_id}
        '''
        result = self._values.get("user_role_template_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_azure#user_ttl DynamicSecretAzure#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretAzureConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretAzure",
    "DynamicSecretAzureConfig",
]

publication.publish()

def _typecheckingstub__0f803fc002dfd10094dbf7371b54d9989409963f27e076b317d8409bdee4692a(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    app_obj_id: typing.Optional[builtins.str] = None,
    azure_client_id: typing.Optional[builtins.str] = None,
    azure_client_secret: typing.Optional[builtins.str] = None,
    azure_tenant_id: typing.Optional[builtins.str] = None,
    custom_username_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_url: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_group_obj_id: typing.Optional[builtins.str] = None,
    user_portal_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    user_principal_name: typing.Optional[builtins.str] = None,
    user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    user_role_template_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__f04f2212f8aa4e76a66f3c23b04a83a693bc29b428ece3a4db6a9a9b850a4e67(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b78b987f98c6ed1349786e9cdc812624d337201b65d7739444c33c13b5f3f64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0de571d94ad2e7148a5b93c9e16091903f3ef3326cda3ce4891877678b5ecd19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5489195aa38c5b9a770bf01a22516f1979f5e304f47931b9db8e98d245484a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d1bc981e0640136dfd01deaa1ab60810ccab6cc4b7524b664a8c84438a1ceac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__743473c415fe4d8c0a9230bb6a45f656ba8c79203564f67f4f54186ec91876b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a60522856bb8de8366582b1aa00fac2673b36f981fb68df8c985f07c7b5bac15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf943c792bc597f9fba51e37e7e9bdfa19c878353187e4154b393ab5d8f60ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4323c9e53c12c2228d8244bbd07f908669183da552cf7af70d578273c321b946(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b8d52652ffc31ace70b31148dd5fa848da3fb96e052ef3b5327997cbba0db48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bfcb568aedcf905228ef18086c7ccd64e210e77d9beec9b461f60cf90b04268(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5cd9820ec425d41b16aa77632cc2c62cb6365cbbe8db2381e574a634d961bdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d0845a309b21b8bcbf0e4b6365ad49b187c06d626ec56361050208538356f9f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b4d4deb12171eccc4b80a76d5e66382b322360088e51461e1f8616943555a80(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e12ef72c15b236f4d3a906ebb5e2657ddd96958c68f453ab1bf6de989b6dd75(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cddeff03d5fe2c1b06a0b01d2fbe05ffc0e23d3f5374a67030fc5a776ba7e19c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__167665c1ff5fab005a3d5049fc2271c034f2fd88fd08feeb0344fcbecc01d6c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__684858e91d7bb0ba93724a980157a807246034173d338f1bb9791b8fd3bdfc19(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aeaa8eca64678023801f190f2526013501a33615795afa9fa64aa6db61100358(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41f9a8ffb72bdedbd75bb1a7369fedadb571e061a7b8c6fd6708d32a5e7f3843(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0656c4cbe8e86fe9f6e7d96389c84c70ce2604d66d81bbc014c0435b41b93be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2835326285de2b979deebc0d3e1d523774a738add9132b794973aed3db177cb5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f9bfb445b64398ea3a349915601ed1ccdf094659a30668667411dee5a13cbc(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    app_obj_id: typing.Optional[builtins.str] = None,
    azure_client_id: typing.Optional[builtins.str] = None,
    azure_client_secret: typing.Optional[builtins.str] = None,
    azure_tenant_id: typing.Optional[builtins.str] = None,
    custom_username_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    password_length: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_url: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_group_obj_id: typing.Optional[builtins.str] = None,
    user_portal_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    user_principal_name: typing.Optional[builtins.str] = None,
    user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    user_role_template_id: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
