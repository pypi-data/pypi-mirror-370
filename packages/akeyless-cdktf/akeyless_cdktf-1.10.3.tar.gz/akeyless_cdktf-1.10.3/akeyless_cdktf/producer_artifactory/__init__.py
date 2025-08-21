'''
# `akeyless_producer_artifactory`

Refer to the Terraform Registry for docs: [`akeyless_producer_artifactory`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory).
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


class ProducerArtifactory(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerArtifactory.ProducerArtifactory",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory akeyless_producer_artifactory}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        artifactory_token_audience: builtins.str,
        artifactory_token_scope: builtins.str,
        name: builtins.str,
        artifactory_admin_name: typing.Optional[builtins.str] = None,
        artifactory_admin_pwd: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory akeyless_producer_artifactory} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param artifactory_token_audience: A space-separate list of the other Artifactory instances or services that should accept this token., for example: jfrt@*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_token_audience ProducerArtifactory#artifactory_token_audience}
        :param artifactory_token_scope: Token scope provided as a space-separated list, for example: member-of-groups:readers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_token_scope ProducerArtifactory#artifactory_token_scope}
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#name ProducerArtifactory#name}
        :param artifactory_admin_name: Admin name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_admin_name ProducerArtifactory#artifactory_admin_name}
        :param artifactory_admin_pwd: Admin API Key/Password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_admin_pwd ProducerArtifactory#artifactory_admin_pwd}
        :param base_url: Artifactory REST URL, must end with artifactory postfix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#base_url ProducerArtifactory#base_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#id ProducerArtifactory#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#producer_encryption_key_name ProducerArtifactory#producer_encryption_key_name}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#tags ProducerArtifactory#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#target_name ProducerArtifactory#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#user_ttl ProducerArtifactory#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1a9428dab25bd7fd4339b3a3e96ea5a679ecda2b1ae76324350289b5318a0d0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerArtifactoryConfig(
            artifactory_token_audience=artifactory_token_audience,
            artifactory_token_scope=artifactory_token_scope,
            name=name,
            artifactory_admin_name=artifactory_admin_name,
            artifactory_admin_pwd=artifactory_admin_pwd,
            base_url=base_url,
            id=id,
            producer_encryption_key_name=producer_encryption_key_name,
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
        '''Generates CDKTF code for importing a ProducerArtifactory resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerArtifactory to import.
        :param import_from_id: The id of the existing ProducerArtifactory that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerArtifactory to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9b7b92213e8c815f3761c9061a47c080c36f05a83377e4111eebe19835b13a6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetArtifactoryAdminName")
    def reset_artifactory_admin_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArtifactoryAdminName", []))

    @jsii.member(jsii_name="resetArtifactoryAdminPwd")
    def reset_artifactory_admin_pwd(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArtifactoryAdminPwd", []))

    @jsii.member(jsii_name="resetBaseUrl")
    def reset_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrl", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

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
    @jsii.member(jsii_name="artifactoryAdminNameInput")
    def artifactory_admin_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactoryAdminNameInput"))

    @builtins.property
    @jsii.member(jsii_name="artifactoryAdminPwdInput")
    def artifactory_admin_pwd_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactoryAdminPwdInput"))

    @builtins.property
    @jsii.member(jsii_name="artifactoryTokenAudienceInput")
    def artifactory_token_audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactoryTokenAudienceInput"))

    @builtins.property
    @jsii.member(jsii_name="artifactoryTokenScopeInput")
    def artifactory_token_scope_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "artifactoryTokenScopeInput"))

    @builtins.property
    @jsii.member(jsii_name="baseUrlInput")
    def base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlInput"))

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
    @jsii.member(jsii_name="artifactoryAdminName")
    def artifactory_admin_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "artifactoryAdminName"))

    @artifactory_admin_name.setter
    def artifactory_admin_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f26f147a8d7c2170712425f80fa96fb0be5aaa1c71eb31b0830b37ea76fa9d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifactoryAdminName", value)

    @builtins.property
    @jsii.member(jsii_name="artifactoryAdminPwd")
    def artifactory_admin_pwd(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "artifactoryAdminPwd"))

    @artifactory_admin_pwd.setter
    def artifactory_admin_pwd(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2359a03214f0f9b065c3e4e0802c8b96d34194f6b1194cbff28bcea9505837e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifactoryAdminPwd", value)

    @builtins.property
    @jsii.member(jsii_name="artifactoryTokenAudience")
    def artifactory_token_audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "artifactoryTokenAudience"))

    @artifactory_token_audience.setter
    def artifactory_token_audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8120fbc321f7583e641af115bf3862d53f1c2c29b0712dd2448dd6f2c04e45d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifactoryTokenAudience", value)

    @builtins.property
    @jsii.member(jsii_name="artifactoryTokenScope")
    def artifactory_token_scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "artifactoryTokenScope"))

    @artifactory_token_scope.setter
    def artifactory_token_scope(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7982c3ccc96e4f674870112975cfbea85d44e0a7056300279b32d0512c0cc559)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "artifactoryTokenScope", value)

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df9a186e09f4c5633ebc35b4e57c2922fc384a07a9df1a539f8d243692c89ab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b5977ffaa05ec43afbdce51742bafc651c4e010efe923a82b3a3ce5b26bbf98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2d6a03a355f38ca7256dd673dbd84284daa0aeda282a136bf17eea78a2f137e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__347079de96ec5f7c15d09b93ef0c244ef3d276ec4308790497c8e9ca6676c88d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7c4e47c6b3afc62539db434ef1df0029fdff44cc199fd10156c0730b21d80e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f46d3d27090795b23204cd8bb3b12ca168e90de9513b27549a7d2a393464409)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ae4902fe96c91bdc9017abc7a4a8e0c28bef0e29bdffe18ccfabb7928e58ab5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerArtifactory.ProducerArtifactoryConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "artifactory_token_audience": "artifactoryTokenAudience",
        "artifactory_token_scope": "artifactoryTokenScope",
        "name": "name",
        "artifactory_admin_name": "artifactoryAdminName",
        "artifactory_admin_pwd": "artifactoryAdminPwd",
        "base_url": "baseUrl",
        "id": "id",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerArtifactoryConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        artifactory_token_audience: builtins.str,
        artifactory_token_scope: builtins.str,
        name: builtins.str,
        artifactory_admin_name: typing.Optional[builtins.str] = None,
        artifactory_admin_pwd: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
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
        :param artifactory_token_audience: A space-separate list of the other Artifactory instances or services that should accept this token., for example: jfrt@*. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_token_audience ProducerArtifactory#artifactory_token_audience}
        :param artifactory_token_scope: Token scope provided as a space-separated list, for example: member-of-groups:readers. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_token_scope ProducerArtifactory#artifactory_token_scope}
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#name ProducerArtifactory#name}
        :param artifactory_admin_name: Admin name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_admin_name ProducerArtifactory#artifactory_admin_name}
        :param artifactory_admin_pwd: Admin API Key/Password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_admin_pwd ProducerArtifactory#artifactory_admin_pwd}
        :param base_url: Artifactory REST URL, must end with artifactory postfix. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#base_url ProducerArtifactory#base_url}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#id ProducerArtifactory#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#producer_encryption_key_name ProducerArtifactory#producer_encryption_key_name}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#tags ProducerArtifactory#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#target_name ProducerArtifactory#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#user_ttl ProducerArtifactory#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__859c995dcec75e52e3478933d5e4ef1be6cf3a6d0f1eec4872cf34d2c63f2332)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument artifactory_token_audience", value=artifactory_token_audience, expected_type=type_hints["artifactory_token_audience"])
            check_type(argname="argument artifactory_token_scope", value=artifactory_token_scope, expected_type=type_hints["artifactory_token_scope"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument artifactory_admin_name", value=artifactory_admin_name, expected_type=type_hints["artifactory_admin_name"])
            check_type(argname="argument artifactory_admin_pwd", value=artifactory_admin_pwd, expected_type=type_hints["artifactory_admin_pwd"])
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument target_name", value=target_name, expected_type=type_hints["target_name"])
            check_type(argname="argument user_ttl", value=user_ttl, expected_type=type_hints["user_ttl"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "artifactory_token_audience": artifactory_token_audience,
            "artifactory_token_scope": artifactory_token_scope,
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
        if artifactory_admin_name is not None:
            self._values["artifactory_admin_name"] = artifactory_admin_name
        if artifactory_admin_pwd is not None:
            self._values["artifactory_admin_pwd"] = artifactory_admin_pwd
        if base_url is not None:
            self._values["base_url"] = base_url
        if id is not None:
            self._values["id"] = id
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
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
    def artifactory_token_audience(self) -> builtins.str:
        '''A space-separate list of the other Artifactory instances or services that should accept this token., for example: jfrt@*.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_token_audience ProducerArtifactory#artifactory_token_audience}
        '''
        result = self._values.get("artifactory_token_audience")
        assert result is not None, "Required property 'artifactory_token_audience' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifactory_token_scope(self) -> builtins.str:
        '''Token scope provided as a space-separated list, for example: member-of-groups:readers.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_token_scope ProducerArtifactory#artifactory_token_scope}
        '''
        result = self._values.get("artifactory_token_scope")
        assert result is not None, "Required property 'artifactory_token_scope' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Producer name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#name ProducerArtifactory#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def artifactory_admin_name(self) -> typing.Optional[builtins.str]:
        '''Admin name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_admin_name ProducerArtifactory#artifactory_admin_name}
        '''
        result = self._values.get("artifactory_admin_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def artifactory_admin_pwd(self) -> typing.Optional[builtins.str]:
        '''Admin API Key/Password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#artifactory_admin_pwd ProducerArtifactory#artifactory_admin_pwd}
        '''
        result = self._values.get("artifactory_admin_pwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''Artifactory REST URL, must end with artifactory postfix.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#base_url ProducerArtifactory#base_url}
        '''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#id ProducerArtifactory#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#producer_encryption_key_name ProducerArtifactory#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#tags ProducerArtifactory#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#target_name ProducerArtifactory#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_artifactory#user_ttl ProducerArtifactory#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerArtifactoryConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerArtifactory",
    "ProducerArtifactoryConfig",
]

publication.publish()

def _typecheckingstub__d1a9428dab25bd7fd4339b3a3e96ea5a679ecda2b1ae76324350289b5318a0d0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    artifactory_token_audience: builtins.str,
    artifactory_token_scope: builtins.str,
    name: builtins.str,
    artifactory_admin_name: typing.Optional[builtins.str] = None,
    artifactory_admin_pwd: typing.Optional[builtins.str] = None,
    base_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d9b7b92213e8c815f3761c9061a47c080c36f05a83377e4111eebe19835b13a6(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f26f147a8d7c2170712425f80fa96fb0be5aaa1c71eb31b0830b37ea76fa9d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2359a03214f0f9b065c3e4e0802c8b96d34194f6b1194cbff28bcea9505837e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8120fbc321f7583e641af115bf3862d53f1c2c29b0712dd2448dd6f2c04e45d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7982c3ccc96e4f674870112975cfbea85d44e0a7056300279b32d0512c0cc559(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df9a186e09f4c5633ebc35b4e57c2922fc384a07a9df1a539f8d243692c89ab2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b5977ffaa05ec43afbdce51742bafc651c4e010efe923a82b3a3ce5b26bbf98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2d6a03a355f38ca7256dd673dbd84284daa0aeda282a136bf17eea78a2f137e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__347079de96ec5f7c15d09b93ef0c244ef3d276ec4308790497c8e9ca6676c88d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7c4e47c6b3afc62539db434ef1df0029fdff44cc199fd10156c0730b21d80e0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f46d3d27090795b23204cd8bb3b12ca168e90de9513b27549a7d2a393464409(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ae4902fe96c91bdc9017abc7a4a8e0c28bef0e29bdffe18ccfabb7928e58ab5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__859c995dcec75e52e3478933d5e4ef1be6cf3a6d0f1eec4872cf34d2c63f2332(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    artifactory_token_audience: builtins.str,
    artifactory_token_scope: builtins.str,
    name: builtins.str,
    artifactory_admin_name: typing.Optional[builtins.str] = None,
    artifactory_admin_pwd: typing.Optional[builtins.str] = None,
    base_url: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
