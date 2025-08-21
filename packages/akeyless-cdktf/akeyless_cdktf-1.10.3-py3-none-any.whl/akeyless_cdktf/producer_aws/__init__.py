'''
# `akeyless_producer_aws`

Refer to the Terraform Registry for docs: [`akeyless_producer_aws`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws).
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


class ProducerAws(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerAws.ProducerAws",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws akeyless_producer_aws}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        access_mode: typing.Optional[builtins.str] = None,
        aws_access_key_id: typing.Optional[builtins.str] = None,
        aws_access_secret_key: typing.Optional[builtins.str] = None,
        aws_role_arns: typing.Optional[builtins.str] = None,
        aws_user_console_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        aws_user_groups: typing.Optional[builtins.str] = None,
        aws_user_policies: typing.Optional[builtins.str] = None,
        aws_user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secure_access_aws_account_id: typing.Optional[builtins.str] = None,
        secure_access_aws_native_cli: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_aws_region: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_url: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws akeyless_producer_aws} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#name ProducerAws#name}
        :param access_mode: The types of credentials to retrieve from AWS. Options:[iam_user,assume_role]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#access_mode ProducerAws#access_mode}
        :param aws_access_key_id: Access Key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_access_key_id ProducerAws#aws_access_key_id}
        :param aws_access_secret_key: Access Secret Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_access_secret_key ProducerAws#aws_access_secret_key}
        :param aws_role_arns: AWS Role ARNs to be use in the Assume Role operation. Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_role_arns ProducerAws#aws_role_arns}
        :param aws_user_console_access: Enable AWS User console access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_console_access ProducerAws#aws_user_console_access}
        :param aws_user_groups: UserGroup name(s). Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_groups ProducerAws#aws_user_groups}
        :param aws_user_policies: Policy ARN(s). Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_policies ProducerAws#aws_user_policies}
        :param aws_user_programmatic_access: Enable AWS User programmatic access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_programmatic_access ProducerAws#aws_user_programmatic_access}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#id ProducerAws#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#producer_encryption_key_name ProducerAws#producer_encryption_key_name}
        :param region: Region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#region ProducerAws#region}
        :param secure_access_aws_account_id: The aws account id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_account_id ProducerAws#secure_access_aws_account_id}
        :param secure_access_aws_native_cli: The aws native cli. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_native_cli ProducerAws#secure_access_aws_native_cli}
        :param secure_access_aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_region ProducerAws#secure_access_aws_region}.
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_bastion_issuer ProducerAws#secure_access_bastion_issuer}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_enable ProducerAws#secure_access_enable}
        :param secure_access_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_url ProducerAws#secure_access_url}.
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_web ProducerAws#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_web_browsing ProducerAws#secure_access_web_browsing}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#tags ProducerAws#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#target_name ProducerAws#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#user_ttl ProducerAws#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__384026deab7811365f41bfb47505272bfaf958790ab2dd823ae3697181ba8677)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerAwsConfig(
            name=name,
            access_mode=access_mode,
            aws_access_key_id=aws_access_key_id,
            aws_access_secret_key=aws_access_secret_key,
            aws_role_arns=aws_role_arns,
            aws_user_console_access=aws_user_console_access,
            aws_user_groups=aws_user_groups,
            aws_user_policies=aws_user_policies,
            aws_user_programmatic_access=aws_user_programmatic_access,
            id=id,
            producer_encryption_key_name=producer_encryption_key_name,
            region=region,
            secure_access_aws_account_id=secure_access_aws_account_id,
            secure_access_aws_native_cli=secure_access_aws_native_cli,
            secure_access_aws_region=secure_access_aws_region,
            secure_access_bastion_issuer=secure_access_bastion_issuer,
            secure_access_enable=secure_access_enable,
            secure_access_url=secure_access_url,
            secure_access_web=secure_access_web,
            secure_access_web_browsing=secure_access_web_browsing,
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
        '''Generates CDKTF code for importing a ProducerAws resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerAws to import.
        :param import_from_id: The id of the existing ProducerAws that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerAws to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__239fbb1c52ebd05aa9bf0f9b20a2fd0d608c3ac05de01d4f81b11913de55b2b5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccessMode")
    def reset_access_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessMode", []))

    @jsii.member(jsii_name="resetAwsAccessKeyId")
    def reset_aws_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccessKeyId", []))

    @jsii.member(jsii_name="resetAwsAccessSecretKey")
    def reset_aws_access_secret_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccessSecretKey", []))

    @jsii.member(jsii_name="resetAwsRoleArns")
    def reset_aws_role_arns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsRoleArns", []))

    @jsii.member(jsii_name="resetAwsUserConsoleAccess")
    def reset_aws_user_console_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsUserConsoleAccess", []))

    @jsii.member(jsii_name="resetAwsUserGroups")
    def reset_aws_user_groups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsUserGroups", []))

    @jsii.member(jsii_name="resetAwsUserPolicies")
    def reset_aws_user_policies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsUserPolicies", []))

    @jsii.member(jsii_name="resetAwsUserProgrammaticAccess")
    def reset_aws_user_programmatic_access(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsUserProgrammaticAccess", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetSecureAccessAwsAccountId")
    def reset_secure_access_aws_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessAwsAccountId", []))

    @jsii.member(jsii_name="resetSecureAccessAwsNativeCli")
    def reset_secure_access_aws_native_cli(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessAwsNativeCli", []))

    @jsii.member(jsii_name="resetSecureAccessAwsRegion")
    def reset_secure_access_aws_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessAwsRegion", []))

    @jsii.member(jsii_name="resetSecureAccessBastionIssuer")
    def reset_secure_access_bastion_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessBastionIssuer", []))

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
    @jsii.member(jsii_name="accessModeInput")
    def access_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessModeInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyIdInput")
    def aws_access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAccessSecretKeyInput")
    def aws_access_secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccessSecretKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="awsRoleArnsInput")
    def aws_role_arns_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsRoleArnsInput"))

    @builtins.property
    @jsii.member(jsii_name="awsUserConsoleAccessInput")
    def aws_user_console_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "awsUserConsoleAccessInput"))

    @builtins.property
    @jsii.member(jsii_name="awsUserGroupsInput")
    def aws_user_groups_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsUserGroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="awsUserPoliciesInput")
    def aws_user_policies_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsUserPoliciesInput"))

    @builtins.property
    @jsii.member(jsii_name="awsUserProgrammaticAccessInput")
    def aws_user_programmatic_access_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "awsUserProgrammaticAccessInput"))

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
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessAwsAccountIdInput")
    def secure_access_aws_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessAwsAccountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessAwsNativeCliInput")
    def secure_access_aws_native_cli_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessAwsNativeCliInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessAwsRegionInput")
    def secure_access_aws_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessAwsRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuerInput")
    def secure_access_bastion_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessBastionIssuerInput"))

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
    @jsii.member(jsii_name="userTtlInput")
    def user_ttl_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userTtlInput"))

    @builtins.property
    @jsii.member(jsii_name="accessMode")
    def access_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessMode"))

    @access_mode.setter
    def access_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad52ca22e09311ea68994fc17bde0ec486ff54c7303f5c40d3c2609bc8f6baea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessMode", value)

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyId")
    def aws_access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccessKeyId"))

    @aws_access_key_id.setter
    def aws_access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2217ed5b8fb13678d3064dc51db40c6c985c27b23bb83f2196b6e3b5b9ede341)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="awsAccessSecretKey")
    def aws_access_secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccessSecretKey"))

    @aws_access_secret_key.setter
    def aws_access_secret_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe529914567048856c836939a0a49cfec0f43b96b003cc2513c0b3fe9dd25c85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessSecretKey", value)

    @builtins.property
    @jsii.member(jsii_name="awsRoleArns")
    def aws_role_arns(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsRoleArns"))

    @aws_role_arns.setter
    def aws_role_arns(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e586b4cd02135087da7df3ab0b10ca0f5e6aa9f54234e1ee537e563a4a12f806)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsRoleArns", value)

    @builtins.property
    @jsii.member(jsii_name="awsUserConsoleAccess")
    def aws_user_console_access(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "awsUserConsoleAccess"))

    @aws_user_console_access.setter
    def aws_user_console_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa8db51e3f9d755ff80ce35af2b3d5b3c7977b00be09c5c1332afa606495fb2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsUserConsoleAccess", value)

    @builtins.property
    @jsii.member(jsii_name="awsUserGroups")
    def aws_user_groups(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsUserGroups"))

    @aws_user_groups.setter
    def aws_user_groups(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd207e426e4aa90235e6bc2bf0b8bd48b89215f7eef0529815f9025104d15733)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsUserGroups", value)

    @builtins.property
    @jsii.member(jsii_name="awsUserPolicies")
    def aws_user_policies(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsUserPolicies"))

    @aws_user_policies.setter
    def aws_user_policies(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3f56f94909127386ea668de02b8da1041c4ea9a8c563b736acca276d340cdb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsUserPolicies", value)

    @builtins.property
    @jsii.member(jsii_name="awsUserProgrammaticAccess")
    def aws_user_programmatic_access(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "awsUserProgrammaticAccess"))

    @aws_user_programmatic_access.setter
    def aws_user_programmatic_access(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c716a987979d3ec56f26b59d1049db839d32ca9ef3b4b627f2f8ea672612663a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsUserProgrammaticAccess", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c709350eecfcc89d83dfc1e4a41c95eb00afd4d73c05f9c570d4a5db97a77772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__223859c24f0d3da98e5b9ca4c8cddd0ff97e995b14135b8d26962f6627672080)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67db571867a912523a4d3d419caa404375a7a5da999cfa1bcea56198ba0e8c05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61a92deaba08c53dcaf3381acc3c95a1b929b007ab936aa94046a087d52201b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessAwsAccountId")
    def secure_access_aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessAwsAccountId"))

    @secure_access_aws_account_id.setter
    def secure_access_aws_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfcd4814fd1058a7c41c1921c8023fe71c9257236694f45b01a4dc3e73df07f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAwsAccountId", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessAwsNativeCli")
    def secure_access_aws_native_cli(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessAwsNativeCli"))

    @secure_access_aws_native_cli.setter
    def secure_access_aws_native_cli(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01781ff555068e001a264072af9e952298be22bc2d370badd7c177c4c7154afd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAwsNativeCli", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessAwsRegion")
    def secure_access_aws_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessAwsRegion"))

    @secure_access_aws_region.setter
    def secure_access_aws_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eda0f2383bc063ccc41decb2957276301fd6709b44e9060e58618c375a6143a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAwsRegion", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99cbfd676007bbe75518fef3e22a73c32f371f7a4a9ceb3ff718d07cbdb49c26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409e6494e9c3c5fb38bbf883c6c0f204c0726bbfac0041608e7852faa2c0926f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessUrl")
    def secure_access_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessUrl"))

    @secure_access_url.setter
    def secure_access_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e18bad20e17af5d87352d3b87cc31bb8675dd9c4ba1a3c2c4670217cf9f7e6d3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b4a42fc438e99b9d08ffcf509153a7a576c318dcbf003a4f312b65f08ccfb99)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b6ea673f4db23786f6be07aff0a2859d6534a0e7081e9cf848e06f5dbcdd6a60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWebBrowsing", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71bd1bb83f737372bf54df34f793d2184f23f6fdca9977dcaed7f5b82cf9939f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e668f7a106126711cb99f4c2c56f56451b825c0d35666710bbd64aeedb267c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01aa374f13282ae1d9c2b31a04169403aa93394f6883da0b5b01055b9b4d5c51)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerAws.ProducerAwsConfig",
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
        "access_mode": "accessMode",
        "aws_access_key_id": "awsAccessKeyId",
        "aws_access_secret_key": "awsAccessSecretKey",
        "aws_role_arns": "awsRoleArns",
        "aws_user_console_access": "awsUserConsoleAccess",
        "aws_user_groups": "awsUserGroups",
        "aws_user_policies": "awsUserPolicies",
        "aws_user_programmatic_access": "awsUserProgrammaticAccess",
        "id": "id",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "region": "region",
        "secure_access_aws_account_id": "secureAccessAwsAccountId",
        "secure_access_aws_native_cli": "secureAccessAwsNativeCli",
        "secure_access_aws_region": "secureAccessAwsRegion",
        "secure_access_bastion_issuer": "secureAccessBastionIssuer",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_url": "secureAccessUrl",
        "secure_access_web": "secureAccessWeb",
        "secure_access_web_browsing": "secureAccessWebBrowsing",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerAwsConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_mode: typing.Optional[builtins.str] = None,
        aws_access_key_id: typing.Optional[builtins.str] = None,
        aws_access_secret_key: typing.Optional[builtins.str] = None,
        aws_role_arns: typing.Optional[builtins.str] = None,
        aws_user_console_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        aws_user_groups: typing.Optional[builtins.str] = None,
        aws_user_policies: typing.Optional[builtins.str] = None,
        aws_user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secure_access_aws_account_id: typing.Optional[builtins.str] = None,
        secure_access_aws_native_cli: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_aws_region: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_url: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#name ProducerAws#name}
        :param access_mode: The types of credentials to retrieve from AWS. Options:[iam_user,assume_role]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#access_mode ProducerAws#access_mode}
        :param aws_access_key_id: Access Key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_access_key_id ProducerAws#aws_access_key_id}
        :param aws_access_secret_key: Access Secret Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_access_secret_key ProducerAws#aws_access_secret_key}
        :param aws_role_arns: AWS Role ARNs to be use in the Assume Role operation. Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_role_arns ProducerAws#aws_role_arns}
        :param aws_user_console_access: Enable AWS User console access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_console_access ProducerAws#aws_user_console_access}
        :param aws_user_groups: UserGroup name(s). Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_groups ProducerAws#aws_user_groups}
        :param aws_user_policies: Policy ARN(s). Multiple values should be separated by comma. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_policies ProducerAws#aws_user_policies}
        :param aws_user_programmatic_access: Enable AWS User programmatic access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_programmatic_access ProducerAws#aws_user_programmatic_access}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#id ProducerAws#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#producer_encryption_key_name ProducerAws#producer_encryption_key_name}
        :param region: Region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#region ProducerAws#region}
        :param secure_access_aws_account_id: The aws account id. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_account_id ProducerAws#secure_access_aws_account_id}
        :param secure_access_aws_native_cli: The aws native cli. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_native_cli ProducerAws#secure_access_aws_native_cli}
        :param secure_access_aws_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_region ProducerAws#secure_access_aws_region}.
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_bastion_issuer ProducerAws#secure_access_bastion_issuer}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_enable ProducerAws#secure_access_enable}
        :param secure_access_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_url ProducerAws#secure_access_url}.
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_web ProducerAws#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_web_browsing ProducerAws#secure_access_web_browsing}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#tags ProducerAws#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#target_name ProducerAws#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#user_ttl ProducerAws#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5851857f7e55d77cdd3264e33637dd877a528aef0d348c088080997d738fe126)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument access_mode", value=access_mode, expected_type=type_hints["access_mode"])
            check_type(argname="argument aws_access_key_id", value=aws_access_key_id, expected_type=type_hints["aws_access_key_id"])
            check_type(argname="argument aws_access_secret_key", value=aws_access_secret_key, expected_type=type_hints["aws_access_secret_key"])
            check_type(argname="argument aws_role_arns", value=aws_role_arns, expected_type=type_hints["aws_role_arns"])
            check_type(argname="argument aws_user_console_access", value=aws_user_console_access, expected_type=type_hints["aws_user_console_access"])
            check_type(argname="argument aws_user_groups", value=aws_user_groups, expected_type=type_hints["aws_user_groups"])
            check_type(argname="argument aws_user_policies", value=aws_user_policies, expected_type=type_hints["aws_user_policies"])
            check_type(argname="argument aws_user_programmatic_access", value=aws_user_programmatic_access, expected_type=type_hints["aws_user_programmatic_access"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument secure_access_aws_account_id", value=secure_access_aws_account_id, expected_type=type_hints["secure_access_aws_account_id"])
            check_type(argname="argument secure_access_aws_native_cli", value=secure_access_aws_native_cli, expected_type=type_hints["secure_access_aws_native_cli"])
            check_type(argname="argument secure_access_aws_region", value=secure_access_aws_region, expected_type=type_hints["secure_access_aws_region"])
            check_type(argname="argument secure_access_bastion_issuer", value=secure_access_bastion_issuer, expected_type=type_hints["secure_access_bastion_issuer"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_url", value=secure_access_url, expected_type=type_hints["secure_access_url"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
            check_type(argname="argument secure_access_web_browsing", value=secure_access_web_browsing, expected_type=type_hints["secure_access_web_browsing"])
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
        if access_mode is not None:
            self._values["access_mode"] = access_mode
        if aws_access_key_id is not None:
            self._values["aws_access_key_id"] = aws_access_key_id
        if aws_access_secret_key is not None:
            self._values["aws_access_secret_key"] = aws_access_secret_key
        if aws_role_arns is not None:
            self._values["aws_role_arns"] = aws_role_arns
        if aws_user_console_access is not None:
            self._values["aws_user_console_access"] = aws_user_console_access
        if aws_user_groups is not None:
            self._values["aws_user_groups"] = aws_user_groups
        if aws_user_policies is not None:
            self._values["aws_user_policies"] = aws_user_policies
        if aws_user_programmatic_access is not None:
            self._values["aws_user_programmatic_access"] = aws_user_programmatic_access
        if id is not None:
            self._values["id"] = id
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
        if region is not None:
            self._values["region"] = region
        if secure_access_aws_account_id is not None:
            self._values["secure_access_aws_account_id"] = secure_access_aws_account_id
        if secure_access_aws_native_cli is not None:
            self._values["secure_access_aws_native_cli"] = secure_access_aws_native_cli
        if secure_access_aws_region is not None:
            self._values["secure_access_aws_region"] = secure_access_aws_region
        if secure_access_bastion_issuer is not None:
            self._values["secure_access_bastion_issuer"] = secure_access_bastion_issuer
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#name ProducerAws#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_mode(self) -> typing.Optional[builtins.str]:
        '''The types of credentials to retrieve from AWS. Options:[iam_user,assume_role].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#access_mode ProducerAws#access_mode}
        '''
        result = self._values.get("access_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_access_key_id(self) -> typing.Optional[builtins.str]:
        '''Access Key ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_access_key_id ProducerAws#aws_access_key_id}
        '''
        result = self._values.get("aws_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_access_secret_key(self) -> typing.Optional[builtins.str]:
        '''Access Secret Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_access_secret_key ProducerAws#aws_access_secret_key}
        '''
        result = self._values.get("aws_access_secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_role_arns(self) -> typing.Optional[builtins.str]:
        '''AWS Role ARNs to be use in the Assume Role operation. Multiple values should be separated by comma.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_role_arns ProducerAws#aws_role_arns}
        '''
        result = self._values.get("aws_role_arns")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_user_console_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable AWS User console access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_console_access ProducerAws#aws_user_console_access}
        '''
        result = self._values.get("aws_user_console_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def aws_user_groups(self) -> typing.Optional[builtins.str]:
        '''UserGroup name(s). Multiple values should be separated by comma.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_groups ProducerAws#aws_user_groups}
        '''
        result = self._values.get("aws_user_groups")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_user_policies(self) -> typing.Optional[builtins.str]:
        '''Policy ARN(s). Multiple values should be separated by comma.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_policies ProducerAws#aws_user_policies}
        '''
        result = self._values.get("aws_user_policies")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_user_programmatic_access(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable AWS User programmatic access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#aws_user_programmatic_access ProducerAws#aws_user_programmatic_access}
        '''
        result = self._values.get("aws_user_programmatic_access")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#id ProducerAws#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#producer_encryption_key_name ProducerAws#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#region ProducerAws#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_aws_account_id(self) -> typing.Optional[builtins.str]:
        '''The aws account id.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_account_id ProducerAws#secure_access_aws_account_id}
        '''
        result = self._values.get("secure_access_aws_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_aws_native_cli(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''The aws native cli.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_native_cli ProducerAws#secure_access_aws_native_cli}
        '''
        result = self._values.get("secure_access_aws_native_cli")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_aws_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_aws_region ProducerAws#secure_access_aws_region}.'''
        result = self._values.get("secure_access_aws_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_bastion_issuer ProducerAws#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_enable ProducerAws#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_url ProducerAws#secure_access_url}.'''
        result = self._values.get("secure_access_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_web ProducerAws#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_web_browsing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Secure browser via Akeyless Web Access Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#secure_access_web_browsing ProducerAws#secure_access_web_browsing}
        '''
        result = self._values.get("secure_access_web_browsing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#tags ProducerAws#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#target_name ProducerAws#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_aws#user_ttl ProducerAws#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerAwsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerAws",
    "ProducerAwsConfig",
]

publication.publish()

def _typecheckingstub__384026deab7811365f41bfb47505272bfaf958790ab2dd823ae3697181ba8677(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    access_mode: typing.Optional[builtins.str] = None,
    aws_access_key_id: typing.Optional[builtins.str] = None,
    aws_access_secret_key: typing.Optional[builtins.str] = None,
    aws_role_arns: typing.Optional[builtins.str] = None,
    aws_user_console_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    aws_user_groups: typing.Optional[builtins.str] = None,
    aws_user_policies: typing.Optional[builtins.str] = None,
    aws_user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    secure_access_aws_account_id: typing.Optional[builtins.str] = None,
    secure_access_aws_native_cli: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_aws_region: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_url: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__239fbb1c52ebd05aa9bf0f9b20a2fd0d608c3ac05de01d4f81b11913de55b2b5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad52ca22e09311ea68994fc17bde0ec486ff54c7303f5c40d3c2609bc8f6baea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2217ed5b8fb13678d3064dc51db40c6c985c27b23bb83f2196b6e3b5b9ede341(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe529914567048856c836939a0a49cfec0f43b96b003cc2513c0b3fe9dd25c85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e586b4cd02135087da7df3ab0b10ca0f5e6aa9f54234e1ee537e563a4a12f806(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa8db51e3f9d755ff80ce35af2b3d5b3c7977b00be09c5c1332afa606495fb2b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd207e426e4aa90235e6bc2bf0b8bd48b89215f7eef0529815f9025104d15733(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3f56f94909127386ea668de02b8da1041c4ea9a8c563b736acca276d340cdb1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c716a987979d3ec56f26b59d1049db839d32ca9ef3b4b627f2f8ea672612663a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c709350eecfcc89d83dfc1e4a41c95eb00afd4d73c05f9c570d4a5db97a77772(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__223859c24f0d3da98e5b9ca4c8cddd0ff97e995b14135b8d26962f6627672080(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67db571867a912523a4d3d419caa404375a7a5da999cfa1bcea56198ba0e8c05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61a92deaba08c53dcaf3381acc3c95a1b929b007ab936aa94046a087d52201b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfcd4814fd1058a7c41c1921c8023fe71c9257236694f45b01a4dc3e73df07f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01781ff555068e001a264072af9e952298be22bc2d370badd7c177c4c7154afd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eda0f2383bc063ccc41decb2957276301fd6709b44e9060e58618c375a6143a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99cbfd676007bbe75518fef3e22a73c32f371f7a4a9ceb3ff718d07cbdb49c26(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409e6494e9c3c5fb38bbf883c6c0f204c0726bbfac0041608e7852faa2c0926f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e18bad20e17af5d87352d3b87cc31bb8675dd9c4ba1a3c2c4670217cf9f7e6d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b4a42fc438e99b9d08ffcf509153a7a576c318dcbf003a4f312b65f08ccfb99(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6ea673f4db23786f6be07aff0a2859d6534a0e7081e9cf848e06f5dbcdd6a60(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71bd1bb83f737372bf54df34f793d2184f23f6fdca9977dcaed7f5b82cf9939f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e668f7a106126711cb99f4c2c56f56451b825c0d35666710bbd64aeedb267c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01aa374f13282ae1d9c2b31a04169403aa93394f6883da0b5b01055b9b4d5c51(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5851857f7e55d77cdd3264e33637dd877a528aef0d348c088080997d738fe126(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    access_mode: typing.Optional[builtins.str] = None,
    aws_access_key_id: typing.Optional[builtins.str] = None,
    aws_access_secret_key: typing.Optional[builtins.str] = None,
    aws_role_arns: typing.Optional[builtins.str] = None,
    aws_user_console_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    aws_user_groups: typing.Optional[builtins.str] = None,
    aws_user_policies: typing.Optional[builtins.str] = None,
    aws_user_programmatic_access: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    secure_access_aws_account_id: typing.Optional[builtins.str] = None,
    secure_access_aws_native_cli: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_aws_region: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_url: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
