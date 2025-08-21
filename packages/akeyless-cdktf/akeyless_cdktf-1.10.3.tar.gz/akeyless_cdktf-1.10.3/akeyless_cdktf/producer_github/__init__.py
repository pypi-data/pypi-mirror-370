'''
# `akeyless_producer_github`

Refer to the Terraform Registry for docs: [`akeyless_producer_github`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github).
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


class ProducerGithub(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerGithub.ProducerGithub",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github akeyless_producer_github}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        github_app_id: typing.Optional[jsii.Number] = None,
        github_app_private_key: typing.Optional[builtins.str] = None,
        github_base_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        installation_id: typing.Optional[jsii.Number] = None,
        installation_repository: typing.Optional[builtins.str] = None,
        target_name: typing.Optional[builtins.str] = None,
        token_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github akeyless_producer_github} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#name ProducerGithub#name}
        :param github_app_id: Github application id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_app_id ProducerGithub#github_app_id}
        :param github_app_private_key: Github application private key (base64 encoded key). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_app_private_key ProducerGithub#github_app_private_key}
        :param github_base_url: Github base url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_base_url ProducerGithub#github_base_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#id ProducerGithub#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param installation_id: Github application installation id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#installation_id ProducerGithub#installation_id}
        :param installation_repository: Optional, instead of installation id, set a GitHub repository '/'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#installation_repository ProducerGithub#installation_repository}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#target_name ProducerGithub#target_name}
        :param token_permissions: Tokens' allowed permissions. By default use installation allowed permissions. Input format: key=value pairs or JSON strings, e.g - -p contents=read -p issues=write or -p '{content:read}' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#token_permissions ProducerGithub#token_permissions}
        :param token_repositories: Tokens' allowed repositories. By default use installation allowed repositories. To specify multiple repositories use argument multiple times: -r RepoName1 -r RepoName2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#token_repositories ProducerGithub#token_repositories}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4734a0cff22d9845935e63eac1d305aca4ea7e2cc921a576ddd50db21dae8efe)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerGithubConfig(
            name=name,
            github_app_id=github_app_id,
            github_app_private_key=github_app_private_key,
            github_base_url=github_base_url,
            id=id,
            installation_id=installation_id,
            installation_repository=installation_repository,
            target_name=target_name,
            token_permissions=token_permissions,
            token_repositories=token_repositories,
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
        '''Generates CDKTF code for importing a ProducerGithub resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerGithub to import.
        :param import_from_id: The id of the existing ProducerGithub that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerGithub to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cba27c8f4a0897bb5fda16132ed9deed1c018301aeb29d87788d1f8cd5b8551)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetGithubAppId")
    def reset_github_app_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGithubAppId", []))

    @jsii.member(jsii_name="resetGithubAppPrivateKey")
    def reset_github_app_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGithubAppPrivateKey", []))

    @jsii.member(jsii_name="resetGithubBaseUrl")
    def reset_github_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGithubBaseUrl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInstallationId")
    def reset_installation_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallationId", []))

    @jsii.member(jsii_name="resetInstallationRepository")
    def reset_installation_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstallationRepository", []))

    @jsii.member(jsii_name="resetTargetName")
    def reset_target_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetName", []))

    @jsii.member(jsii_name="resetTokenPermissions")
    def reset_token_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenPermissions", []))

    @jsii.member(jsii_name="resetTokenRepositories")
    def reset_token_repositories(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenRepositories", []))

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
    @jsii.member(jsii_name="githubAppIdInput")
    def github_app_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "githubAppIdInput"))

    @builtins.property
    @jsii.member(jsii_name="githubAppPrivateKeyInput")
    def github_app_private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "githubAppPrivateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="githubBaseUrlInput")
    def github_base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "githubBaseUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="installationIdInput")
    def installation_id_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "installationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="installationRepositoryInput")
    def installation_repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "installationRepositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="targetNameInput")
    def target_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenPermissionsInput")
    def token_permissions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tokenPermissionsInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenRepositoriesInput")
    def token_repositories_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tokenRepositoriesInput"))

    @builtins.property
    @jsii.member(jsii_name="githubAppId")
    def github_app_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "githubAppId"))

    @github_app_id.setter
    def github_app_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28f0ce0315e815b1b8eb295092064aead536c88f2f44209a22fcd252764fbde2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "githubAppId", value)

    @builtins.property
    @jsii.member(jsii_name="githubAppPrivateKey")
    def github_app_private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "githubAppPrivateKey"))

    @github_app_private_key.setter
    def github_app_private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__749e03ee7cd0ebb5957eaa11a6d35328071ef6f92474e34bebdac72110900e54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "githubAppPrivateKey", value)

    @builtins.property
    @jsii.member(jsii_name="githubBaseUrl")
    def github_base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "githubBaseUrl"))

    @github_base_url.setter
    def github_base_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__727e7c392886991b2a36901b8ea2118cf996e80fc2800efffc13a6bc105c8942)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "githubBaseUrl", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bac23ee47f74ac33491941725de41827931dee7b6d866286bb328199427ead3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="installationId")
    def installation_id(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "installationId"))

    @installation_id.setter
    def installation_id(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91a08261b45e23dc14b491db615a8fee9a102911a6dce4dcb80d1215e36eb139)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "installationId", value)

    @builtins.property
    @jsii.member(jsii_name="installationRepository")
    def installation_repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "installationRepository"))

    @installation_repository.setter
    def installation_repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c29ae2fb6e35e3bcfe00bbf8740918a7c5b533e337d1d5360d35628a794d5d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "installationRepository", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ab2837982016dd221bcf67b99e37972c9e0eb88cbc91b3ffd4c7629c833a10e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c05b7cab652c337b534e9829d8e9ccf5f4f9dce4f2cd36d71d863133c1fd6e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="tokenPermissions")
    def token_permissions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenPermissions"))

    @token_permissions.setter
    def token_permissions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9878fba1e3a34f87162de1b142b5ace6c03907b3e8b6c12e680d2eb3b75e351b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenPermissions", value)

    @builtins.property
    @jsii.member(jsii_name="tokenRepositories")
    def token_repositories(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tokenRepositories"))

    @token_repositories.setter
    def token_repositories(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__502d9c74e9dbe749296e12e5a09f719b11b0e4aeadaf676f0cc65f1850409f3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenRepositories", value)


@jsii.data_type(
    jsii_type="akeyless.producerGithub.ProducerGithubConfig",
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
        "github_app_id": "githubAppId",
        "github_app_private_key": "githubAppPrivateKey",
        "github_base_url": "githubBaseUrl",
        "id": "id",
        "installation_id": "installationId",
        "installation_repository": "installationRepository",
        "target_name": "targetName",
        "token_permissions": "tokenPermissions",
        "token_repositories": "tokenRepositories",
    },
)
class ProducerGithubConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        github_app_id: typing.Optional[jsii.Number] = None,
        github_app_private_key: typing.Optional[builtins.str] = None,
        github_base_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        installation_id: typing.Optional[jsii.Number] = None,
        installation_repository: typing.Optional[builtins.str] = None,
        target_name: typing.Optional[builtins.str] = None,
        token_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
        token_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#name ProducerGithub#name}
        :param github_app_id: Github application id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_app_id ProducerGithub#github_app_id}
        :param github_app_private_key: Github application private key (base64 encoded key). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_app_private_key ProducerGithub#github_app_private_key}
        :param github_base_url: Github base url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_base_url ProducerGithub#github_base_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#id ProducerGithub#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param installation_id: Github application installation id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#installation_id ProducerGithub#installation_id}
        :param installation_repository: Optional, instead of installation id, set a GitHub repository '/'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#installation_repository ProducerGithub#installation_repository}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#target_name ProducerGithub#target_name}
        :param token_permissions: Tokens' allowed permissions. By default use installation allowed permissions. Input format: key=value pairs or JSON strings, e.g - -p contents=read -p issues=write or -p '{content:read}' Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#token_permissions ProducerGithub#token_permissions}
        :param token_repositories: Tokens' allowed repositories. By default use installation allowed repositories. To specify multiple repositories use argument multiple times: -r RepoName1 -r RepoName2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#token_repositories ProducerGithub#token_repositories}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__920cfebe8a2b862007d49ae0650e433356b39ec881030dcd5b7cf5b22e982bca)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument github_app_id", value=github_app_id, expected_type=type_hints["github_app_id"])
            check_type(argname="argument github_app_private_key", value=github_app_private_key, expected_type=type_hints["github_app_private_key"])
            check_type(argname="argument github_base_url", value=github_base_url, expected_type=type_hints["github_base_url"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument installation_id", value=installation_id, expected_type=type_hints["installation_id"])
            check_type(argname="argument installation_repository", value=installation_repository, expected_type=type_hints["installation_repository"])
            check_type(argname="argument target_name", value=target_name, expected_type=type_hints["target_name"])
            check_type(argname="argument token_permissions", value=token_permissions, expected_type=type_hints["token_permissions"])
            check_type(argname="argument token_repositories", value=token_repositories, expected_type=type_hints["token_repositories"])
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
        if github_app_id is not None:
            self._values["github_app_id"] = github_app_id
        if github_app_private_key is not None:
            self._values["github_app_private_key"] = github_app_private_key
        if github_base_url is not None:
            self._values["github_base_url"] = github_base_url
        if id is not None:
            self._values["id"] = id
        if installation_id is not None:
            self._values["installation_id"] = installation_id
        if installation_repository is not None:
            self._values["installation_repository"] = installation_repository
        if target_name is not None:
            self._values["target_name"] = target_name
        if token_permissions is not None:
            self._values["token_permissions"] = token_permissions
        if token_repositories is not None:
            self._values["token_repositories"] = token_repositories

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#name ProducerGithub#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def github_app_id(self) -> typing.Optional[jsii.Number]:
        '''Github application id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_app_id ProducerGithub#github_app_id}
        '''
        result = self._values.get("github_app_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def github_app_private_key(self) -> typing.Optional[builtins.str]:
        '''Github application private key (base64 encoded key).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_app_private_key ProducerGithub#github_app_private_key}
        '''
        result = self._values.get("github_app_private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def github_base_url(self) -> typing.Optional[builtins.str]:
        '''Github base url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#github_base_url ProducerGithub#github_base_url}
        '''
        result = self._values.get("github_base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#id ProducerGithub#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def installation_id(self) -> typing.Optional[jsii.Number]:
        '''Github application installation id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#installation_id ProducerGithub#installation_id}
        '''
        result = self._values.get("installation_id")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def installation_repository(self) -> typing.Optional[builtins.str]:
        '''Optional, instead of installation id, set a GitHub repository '/'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#installation_repository ProducerGithub#installation_repository}
        '''
        result = self._values.get("installation_repository")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#target_name ProducerGithub#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_permissions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Tokens' allowed permissions.

        By default use installation allowed permissions. Input format: key=value pairs or JSON strings, e.g - -p contents=read -p issues=write or -p '{content:read}'

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#token_permissions ProducerGithub#token_permissions}
        '''
        result = self._values.get("token_permissions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def token_repositories(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Tokens' allowed repositories.

        By default use installation allowed repositories. To specify multiple repositories use argument multiple times: -r RepoName1 -r RepoName2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_github#token_repositories ProducerGithub#token_repositories}
        '''
        result = self._values.get("token_repositories")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerGithubConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerGithub",
    "ProducerGithubConfig",
]

publication.publish()

def _typecheckingstub__4734a0cff22d9845935e63eac1d305aca4ea7e2cc921a576ddd50db21dae8efe(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    github_app_id: typing.Optional[jsii.Number] = None,
    github_app_private_key: typing.Optional[builtins.str] = None,
    github_base_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    installation_id: typing.Optional[jsii.Number] = None,
    installation_repository: typing.Optional[builtins.str] = None,
    target_name: typing.Optional[builtins.str] = None,
    token_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__7cba27c8f4a0897bb5fda16132ed9deed1c018301aeb29d87788d1f8cd5b8551(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28f0ce0315e815b1b8eb295092064aead536c88f2f44209a22fcd252764fbde2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__749e03ee7cd0ebb5957eaa11a6d35328071ef6f92474e34bebdac72110900e54(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__727e7c392886991b2a36901b8ea2118cf996e80fc2800efffc13a6bc105c8942(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bac23ee47f74ac33491941725de41827931dee7b6d866286bb328199427ead3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91a08261b45e23dc14b491db615a8fee9a102911a6dce4dcb80d1215e36eb139(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c29ae2fb6e35e3bcfe00bbf8740918a7c5b533e337d1d5360d35628a794d5d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ab2837982016dd221bcf67b99e37972c9e0eb88cbc91b3ffd4c7629c833a10e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c05b7cab652c337b534e9829d8e9ccf5f4f9dce4f2cd36d71d863133c1fd6e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9878fba1e3a34f87162de1b142b5ace6c03907b3e8b6c12e680d2eb3b75e351b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__502d9c74e9dbe749296e12e5a09f719b11b0e4aeadaf676f0cc65f1850409f3d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__920cfebe8a2b862007d49ae0650e433356b39ec881030dcd5b7cf5b22e982bca(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    github_app_id: typing.Optional[jsii.Number] = None,
    github_app_private_key: typing.Optional[builtins.str] = None,
    github_base_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    installation_id: typing.Optional[jsii.Number] = None,
    installation_repository: typing.Optional[builtins.str] = None,
    target_name: typing.Optional[builtins.str] = None,
    token_permissions: typing.Optional[typing.Sequence[builtins.str]] = None,
    token_repositories: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass
