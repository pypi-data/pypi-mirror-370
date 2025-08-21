'''
# `akeyless_dynamic_secret_gitlab`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_gitlab`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab).
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


class DynamicSecretGitlab(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretGitlab.DynamicSecretGitlab",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab akeyless_dynamic_secret_gitlab}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        gitlab_access_token: typing.Optional[builtins.str] = None,
        gitlab_access_type: typing.Optional[builtins.str] = None,
        gitlab_certificate: typing.Optional[builtins.str] = None,
        gitlab_role: typing.Optional[builtins.str] = None,
        gitlab_token_scopes: typing.Optional[builtins.str] = None,
        gitlab_url: typing.Optional[builtins.str] = None,
        group_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        installation_organization: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab akeyless_dynamic_secret_gitlab} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#name DynamicSecretGitlab#name}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#delete_protection DynamicSecretGitlab#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#description DynamicSecretGitlab#description}
        :param gitlab_access_token: Gitlab access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_access_token DynamicSecretGitlab#gitlab_access_token}
        :param gitlab_access_type: Gitlab access token type [project,group]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_access_type DynamicSecretGitlab#gitlab_access_type}
        :param gitlab_certificate: Gitlab tls certificate (base64 encoded). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_certificate DynamicSecretGitlab#gitlab_certificate}
        :param gitlab_role: Gitlab role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_role DynamicSecretGitlab#gitlab_role}
        :param gitlab_token_scopes: Comma-separated list of access token scopes to grant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_token_scopes DynamicSecretGitlab#gitlab_token_scopes}
        :param gitlab_url: Gitlab base url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_url DynamicSecretGitlab#gitlab_url}
        :param group_name: Gitlab group name, required for access-type=group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#group_name DynamicSecretGitlab#group_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#id DynamicSecretGitlab#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param installation_organization: Gitlab project name, required for access-type=project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#installation_organization DynamicSecretGitlab#installation_organization}
        :param tags: A comma-separated list of tags attached to this secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#tags DynamicSecretGitlab#tags}
        :param target_name: Name of an existing target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#target_name DynamicSecretGitlab#target_name}
        :param ttl: Access Token TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#ttl DynamicSecretGitlab#ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af4eccd485ceaffecc33bb9907d66e2b6182bc6be53a4c8e1445e4f60f46efd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretGitlabConfig(
            name=name,
            delete_protection=delete_protection,
            description=description,
            gitlab_access_token=gitlab_access_token,
            gitlab_access_type=gitlab_access_type,
            gitlab_certificate=gitlab_certificate,
            gitlab_role=gitlab_role,
            gitlab_token_scopes=gitlab_token_scopes,
            gitlab_url=gitlab_url,
            group_name=group_name,
            id=id,
            installation_organization=installation_organization,
            tags=tags,
            target_name=target_name,
            ttl=ttl,
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
        '''Generates CDKTF code for importing a DynamicSecretGitlab resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretGitlab to import.
        :param import_from_id: The id of the existing DynamicSecretGitlab that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretGitlab to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aea86a362bc3d1de49f58dca771d9f0c183111ed44c8b9114e637692fe52511)
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

    @jsii.member(jsii_name="resetGitlabAccessToken")
    def reset_gitlab_access_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGitlabAccessToken", []))

    @jsii.member(jsii_name="resetGitlabAccessType")
    def reset_gitlab_access_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGitlabAccessType", []))

    @jsii.member(jsii_name="resetGitlabCertificate")
    def reset_gitlab_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGitlabCertificate", []))

    @jsii.member(jsii_name="resetGitlabRole")
    def reset_gitlab_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGitlabRole", []))

    @jsii.member(jsii_name="resetGitlabTokenScopes")
    def reset_gitlab_token_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGitlabTokenScopes", []))

    @jsii.member(jsii_name="resetGitlabUrl")
    def reset_gitlab_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGitlabUrl", []))

    @jsii.member(jsii_name="resetGroupName")
    def reset_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstallationOrganization")
    def reset_installation_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallationOrganization", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTargetName")
    def reset_target_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetName", []))

    @jsii.member(jsii_name="resetTtl")
    def reset_ttl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTtl", []))

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
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="gitlabAccessTokenInput")
    def gitlab_access_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitlabAccessTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="gitlabAccessTypeInput")
    def gitlab_access_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitlabAccessTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="gitlabCertificateInput")
    def gitlab_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitlabCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="gitlabRoleInput")
    def gitlab_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitlabRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="gitlabTokenScopesInput")
    def gitlab_token_scopes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitlabTokenScopesInput"))

    @builtins.property
    @jsii.member(jsii_name="gitlabUrlInput")
    def gitlab_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gitlabUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="groupNameInput")
    def group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="installationOrganizationInput")
    def installation_organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "installationOrganizationInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="ttlInput")
    def ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ttlInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b0e3fddc842cd567fe9d91fac3ce3e0074a75d88a8a751db28deba74d000acd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4bdebc9f9e260cd38648128460c28fbc401218e3d018d3a15be58d920f42008)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="gitlabAccessToken")
    def gitlab_access_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitlabAccessToken"))

    @gitlab_access_token.setter
    def gitlab_access_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0256902690b1e5f0f6772d6b30c41b41ae335b263b9e98fcc8afd1cfacf8fdf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitlabAccessToken", value)

    @builtins.property
    @jsii.member(jsii_name="gitlabAccessType")
    def gitlab_access_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitlabAccessType"))

    @gitlab_access_type.setter
    def gitlab_access_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0af3361cd1bcc6fae2e983823c72a9a656d2f62e1edf030299448db5a3651fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitlabAccessType", value)

    @builtins.property
    @jsii.member(jsii_name="gitlabCertificate")
    def gitlab_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitlabCertificate"))

    @gitlab_certificate.setter
    def gitlab_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24b47829e6aa33754749d2a961a84e36b97d97212eadde1785667be32ab15d9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitlabCertificate", value)

    @builtins.property
    @jsii.member(jsii_name="gitlabRole")
    def gitlab_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitlabRole"))

    @gitlab_role.setter
    def gitlab_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c90922073baaafcb2f47a06123ddafeaa2e00a88c4d475d539e713b42a8c2175)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitlabRole", value)

    @builtins.property
    @jsii.member(jsii_name="gitlabTokenScopes")
    def gitlab_token_scopes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitlabTokenScopes"))

    @gitlab_token_scopes.setter
    def gitlab_token_scopes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dfe6be0dab2cb44d85f40970f552ee7c967fc72ec55f6b758e83f039f0fe615)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitlabTokenScopes", value)

    @builtins.property
    @jsii.member(jsii_name="gitlabUrl")
    def gitlab_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gitlabUrl"))

    @gitlab_url.setter
    def gitlab_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aee915985605e998004fe67061f8734264bc37817e491ea734675fe3e129c677)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gitlabUrl", value)

    @builtins.property
    @jsii.member(jsii_name="groupName")
    def group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupName"))

    @group_name.setter
    def group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d44cb10ef1ae9fe0cd86b2dddb844efe5e33cff2c8f748119ad9170b8cbe1e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b640784222794312897e60e77d12f8977be7e99ca0c1995e716c529c81690dee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="installationOrganization")
    def installation_organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "installationOrganization"))

    @installation_organization.setter
    def installation_organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29234769b685a763f1ea56881c749d6254cb106d5064a5f96a2966fac66f9ba9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "installationOrganization", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6fdc2e035f0950c3a5f533d66ef0373f037dc775cd6fc701e1405252267cdcd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7bf18b0b49618cbd674d070d6b5edb6e67566a0948bc7b0d71dd6b758c82c13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66046d3da596451afc86aaf6eb4f489428fac9e6f58c8cb7a857cb293a558059)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="ttl")
    def ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ttl"))

    @ttl.setter
    def ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7677840a3be76822e6d1588eedbc5c41e2f323d6eae335ded12ab0222f0d07e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ttl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretGitlab.DynamicSecretGitlabConfig",
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
        "delete_protection": "deleteProtection",
        "description": "description",
        "gitlab_access_token": "gitlabAccessToken",
        "gitlab_access_type": "gitlabAccessType",
        "gitlab_certificate": "gitlabCertificate",
        "gitlab_role": "gitlabRole",
        "gitlab_token_scopes": "gitlabTokenScopes",
        "gitlab_url": "gitlabUrl",
        "group_name": "groupName",
        "id": "id",
        "installation_organization": "installationOrganization",
        "tags": "tags",
        "target_name": "targetName",
        "ttl": "ttl",
    },
)
class DynamicSecretGitlabConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        gitlab_access_token: typing.Optional[builtins.str] = None,
        gitlab_access_type: typing.Optional[builtins.str] = None,
        gitlab_certificate: typing.Optional[builtins.str] = None,
        gitlab_role: typing.Optional[builtins.str] = None,
        gitlab_token_scopes: typing.Optional[builtins.str] = None,
        gitlab_url: typing.Optional[builtins.str] = None,
        group_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        installation_organization: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        target_name: typing.Optional[builtins.str] = None,
        ttl: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#name DynamicSecretGitlab#name}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#delete_protection DynamicSecretGitlab#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#description DynamicSecretGitlab#description}
        :param gitlab_access_token: Gitlab access token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_access_token DynamicSecretGitlab#gitlab_access_token}
        :param gitlab_access_type: Gitlab access token type [project,group]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_access_type DynamicSecretGitlab#gitlab_access_type}
        :param gitlab_certificate: Gitlab tls certificate (base64 encoded). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_certificate DynamicSecretGitlab#gitlab_certificate}
        :param gitlab_role: Gitlab role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_role DynamicSecretGitlab#gitlab_role}
        :param gitlab_token_scopes: Comma-separated list of access token scopes to grant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_token_scopes DynamicSecretGitlab#gitlab_token_scopes}
        :param gitlab_url: Gitlab base url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_url DynamicSecretGitlab#gitlab_url}
        :param group_name: Gitlab group name, required for access-type=group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#group_name DynamicSecretGitlab#group_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#id DynamicSecretGitlab#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param installation_organization: Gitlab project name, required for access-type=project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#installation_organization DynamicSecretGitlab#installation_organization}
        :param tags: A comma-separated list of tags attached to this secret. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#tags DynamicSecretGitlab#tags}
        :param target_name: Name of an existing target. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#target_name DynamicSecretGitlab#target_name}
        :param ttl: Access Token TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#ttl DynamicSecretGitlab#ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83171c5c70cc279122cb53f603a728e8677654b92300d6d3a2229eb84be47dec)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument gitlab_access_token", value=gitlab_access_token, expected_type=type_hints["gitlab_access_token"])
            check_type(argname="argument gitlab_access_type", value=gitlab_access_type, expected_type=type_hints["gitlab_access_type"])
            check_type(argname="argument gitlab_certificate", value=gitlab_certificate, expected_type=type_hints["gitlab_certificate"])
            check_type(argname="argument gitlab_role", value=gitlab_role, expected_type=type_hints["gitlab_role"])
            check_type(argname="argument gitlab_token_scopes", value=gitlab_token_scopes, expected_type=type_hints["gitlab_token_scopes"])
            check_type(argname="argument gitlab_url", value=gitlab_url, expected_type=type_hints["gitlab_url"])
            check_type(argname="argument group_name", value=group_name, expected_type=type_hints["group_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument installation_organization", value=installation_organization, expected_type=type_hints["installation_organization"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument target_name", value=target_name, expected_type=type_hints["target_name"])
            check_type(argname="argument ttl", value=ttl, expected_type=type_hints["ttl"])
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
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if gitlab_access_token is not None:
            self._values["gitlab_access_token"] = gitlab_access_token
        if gitlab_access_type is not None:
            self._values["gitlab_access_type"] = gitlab_access_type
        if gitlab_certificate is not None:
            self._values["gitlab_certificate"] = gitlab_certificate
        if gitlab_role is not None:
            self._values["gitlab_role"] = gitlab_role
        if gitlab_token_scopes is not None:
            self._values["gitlab_token_scopes"] = gitlab_token_scopes
        if gitlab_url is not None:
            self._values["gitlab_url"] = gitlab_url
        if group_name is not None:
            self._values["group_name"] = group_name
        if id is not None:
            self._values["id"] = id
        if installation_organization is not None:
            self._values["installation_organization"] = installation_organization
        if tags is not None:
            self._values["tags"] = tags
        if target_name is not None:
            self._values["target_name"] = target_name
        if ttl is not None:
            self._values["ttl"] = ttl

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#name DynamicSecretGitlab#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this item, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#delete_protection DynamicSecretGitlab#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#description DynamicSecretGitlab#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_access_token(self) -> typing.Optional[builtins.str]:
        '''Gitlab access token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_access_token DynamicSecretGitlab#gitlab_access_token}
        '''
        result = self._values.get("gitlab_access_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_access_type(self) -> typing.Optional[builtins.str]:
        '''Gitlab access token type [project,group].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_access_type DynamicSecretGitlab#gitlab_access_type}
        '''
        result = self._values.get("gitlab_access_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_certificate(self) -> typing.Optional[builtins.str]:
        '''Gitlab tls certificate (base64 encoded).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_certificate DynamicSecretGitlab#gitlab_certificate}
        '''
        result = self._values.get("gitlab_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_role(self) -> typing.Optional[builtins.str]:
        '''Gitlab role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_role DynamicSecretGitlab#gitlab_role}
        '''
        result = self._values.get("gitlab_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_token_scopes(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of access token scopes to grant.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_token_scopes DynamicSecretGitlab#gitlab_token_scopes}
        '''
        result = self._values.get("gitlab_token_scopes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gitlab_url(self) -> typing.Optional[builtins.str]:
        '''Gitlab base url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#gitlab_url DynamicSecretGitlab#gitlab_url}
        '''
        result = self._values.get("gitlab_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_name(self) -> typing.Optional[builtins.str]:
        '''Gitlab group name, required for access-type=group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#group_name DynamicSecretGitlab#group_name}
        '''
        result = self._values.get("group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#id DynamicSecretGitlab#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def installation_organization(self) -> typing.Optional[builtins.str]:
        '''Gitlab project name, required for access-type=project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#installation_organization DynamicSecretGitlab#installation_organization}
        '''
        result = self._values.get("installation_organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A comma-separated list of tags attached to this secret.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#tags DynamicSecretGitlab#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of an existing target.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#target_name DynamicSecretGitlab#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ttl(self) -> typing.Optional[builtins.str]:
        '''Access Token TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gitlab#ttl DynamicSecretGitlab#ttl}
        '''
        result = self._values.get("ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretGitlabConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretGitlab",
    "DynamicSecretGitlabConfig",
]

publication.publish()

def _typecheckingstub__1af4eccd485ceaffecc33bb9907d66e2b6182bc6be53a4c8e1445e4f60f46efd(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    gitlab_access_token: typing.Optional[builtins.str] = None,
    gitlab_access_type: typing.Optional[builtins.str] = None,
    gitlab_certificate: typing.Optional[builtins.str] = None,
    gitlab_role: typing.Optional[builtins.str] = None,
    gitlab_token_scopes: typing.Optional[builtins.str] = None,
    gitlab_url: typing.Optional[builtins.str] = None,
    group_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    installation_organization: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__3aea86a362bc3d1de49f58dca771d9f0c183111ed44c8b9114e637692fe52511(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b0e3fddc842cd567fe9d91fac3ce3e0074a75d88a8a751db28deba74d000acd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4bdebc9f9e260cd38648128460c28fbc401218e3d018d3a15be58d920f42008(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0256902690b1e5f0f6772d6b30c41b41ae335b263b9e98fcc8afd1cfacf8fdf7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0af3361cd1bcc6fae2e983823c72a9a656d2f62e1edf030299448db5a3651fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24b47829e6aa33754749d2a961a84e36b97d97212eadde1785667be32ab15d9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c90922073baaafcb2f47a06123ddafeaa2e00a88c4d475d539e713b42a8c2175(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dfe6be0dab2cb44d85f40970f552ee7c967fc72ec55f6b758e83f039f0fe615(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aee915985605e998004fe67061f8734264bc37817e491ea734675fe3e129c677(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d44cb10ef1ae9fe0cd86b2dddb844efe5e33cff2c8f748119ad9170b8cbe1e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b640784222794312897e60e77d12f8977be7e99ca0c1995e716c529c81690dee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29234769b685a763f1ea56881c749d6254cb106d5064a5f96a2966fac66f9ba9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6fdc2e035f0950c3a5f533d66ef0373f037dc775cd6fc701e1405252267cdcd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7bf18b0b49618cbd674d070d6b5edb6e67566a0948bc7b0d71dd6b758c82c13(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66046d3da596451afc86aaf6eb4f489428fac9e6f58c8cb7a857cb293a558059(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7677840a3be76822e6d1588eedbc5c41e2f323d6eae335ded12ab0222f0d07e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83171c5c70cc279122cb53f603a728e8677654b92300d6d3a2229eb84be47dec(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    gitlab_access_token: typing.Optional[builtins.str] = None,
    gitlab_access_type: typing.Optional[builtins.str] = None,
    gitlab_certificate: typing.Optional[builtins.str] = None,
    gitlab_role: typing.Optional[builtins.str] = None,
    gitlab_token_scopes: typing.Optional[builtins.str] = None,
    gitlab_url: typing.Optional[builtins.str] = None,
    group_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    installation_organization: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
