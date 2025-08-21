'''
# `provider`

Refer to the Terraform Registry for docs: [`akeyless`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs).
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


class AkeylessProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.provider.AkeylessProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs akeyless}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        api_gateway_address: typing.Optional[builtins.str] = None,
        api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderApiKeyLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderAwsIamLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderAzureAdLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderCertLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderEmailLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderGcpLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderJwtLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        token_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderTokenLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderUidLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs akeyless} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#alias AkeylessProvider#alias}
        :param api_gateway_address: Origin URL of the API Gateway server. This is a URL with a scheme, a hostname and a port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#api_gateway_address AkeylessProvider#api_gateway_address}
        :param api_key_login: api_key_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#api_key_login AkeylessProvider#api_key_login}
        :param aws_iam_login: aws_iam_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#aws_iam_login AkeylessProvider#aws_iam_login}
        :param azure_ad_login: azure_ad_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#azure_ad_login AkeylessProvider#azure_ad_login}
        :param cert_login: cert_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#cert_login AkeylessProvider#cert_login}
        :param email_login: email_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#email_login AkeylessProvider#email_login}
        :param gcp_login: gcp_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#gcp_login AkeylessProvider#gcp_login}
        :param jwt_login: jwt_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#jwt_login AkeylessProvider#jwt_login}
        :param token_login: token_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#token_login AkeylessProvider#token_login}
        :param uid_login: uid_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#uid_login AkeylessProvider#uid_login}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8240bb7e189c60a5103b8e54843e452d0c83f7633d1c8a792f0d65a9b3b45e22)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AkeylessProviderConfig(
            alias=alias,
            api_gateway_address=api_gateway_address,
            api_key_login=api_key_login,
            aws_iam_login=aws_iam_login,
            azure_ad_login=azure_ad_login,
            cert_login=cert_login,
            email_login=email_login,
            gcp_login=gcp_login,
            jwt_login=jwt_login,
            token_login=token_login,
            uid_login=uid_login,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a AkeylessProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AkeylessProvider to import.
        :param import_from_id: The id of the existing AkeylessProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AkeylessProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b947e5ea64dd00e53a3fde6bb400724bff69aaf6f908f3064b7908704e489e40)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetApiGatewayAddress")
    def reset_api_gateway_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiGatewayAddress", []))

    @jsii.member(jsii_name="resetApiKeyLogin")
    def reset_api_key_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeyLogin", []))

    @jsii.member(jsii_name="resetAwsIamLogin")
    def reset_aws_iam_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsIamLogin", []))

    @jsii.member(jsii_name="resetAzureAdLogin")
    def reset_azure_ad_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAdLogin", []))

    @jsii.member(jsii_name="resetCertLogin")
    def reset_cert_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertLogin", []))

    @jsii.member(jsii_name="resetEmailLogin")
    def reset_email_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailLogin", []))

    @jsii.member(jsii_name="resetGcpLogin")
    def reset_gcp_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpLogin", []))

    @jsii.member(jsii_name="resetJwtLogin")
    def reset_jwt_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtLogin", []))

    @jsii.member(jsii_name="resetTokenLogin")
    def reset_token_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenLogin", []))

    @jsii.member(jsii_name="resetUidLogin")
    def reset_uid_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUidLogin", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="apiGatewayAddressInput")
    def api_gateway_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiGatewayAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyLoginInput")
    def api_key_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderApiKeyLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderApiKeyLogin"]]], jsii.get(self, "apiKeyLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="awsIamLoginInput")
    def aws_iam_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAwsIamLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAwsIamLogin"]]], jsii.get(self, "awsIamLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdLoginInput")
    def azure_ad_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAzureAdLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAzureAdLogin"]]], jsii.get(self, "azureAdLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="certLoginInput")
    def cert_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderCertLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderCertLogin"]]], jsii.get(self, "certLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="emailLoginInput")
    def email_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderEmailLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderEmailLogin"]]], jsii.get(self, "emailLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpLoginInput")
    def gcp_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderGcpLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderGcpLogin"]]], jsii.get(self, "gcpLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtLoginInput")
    def jwt_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderJwtLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderJwtLogin"]]], jsii.get(self, "jwtLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenLoginInput")
    def token_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderTokenLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderTokenLogin"]]], jsii.get(self, "tokenLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="uidLoginInput")
    def uid_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderUidLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderUidLogin"]]], jsii.get(self, "uidLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e81779c21704bf2442180c0cec8a8c32de6f42c7d3b864e5e0a436a41d2f0a72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value)

    @builtins.property
    @jsii.member(jsii_name="apiGatewayAddress")
    def api_gateway_address(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiGatewayAddress"))

    @api_gateway_address.setter
    def api_gateway_address(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a42f2358ae72aa39a9ffeeb5b42816c13dd91dcfb46e3e847f8b67cffcbfb08e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiGatewayAddress", value)

    @builtins.property
    @jsii.member(jsii_name="apiKeyLogin")
    def api_key_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderApiKeyLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderApiKeyLogin"]]], jsii.get(self, "apiKeyLogin"))

    @api_key_login.setter
    def api_key_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderApiKeyLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20e32050dbaf6cf3b3b6f47c39a8661b65b63ea9978f108f35a1ea91828ee730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKeyLogin", value)

    @builtins.property
    @jsii.member(jsii_name="awsIamLogin")
    def aws_iam_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAwsIamLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAwsIamLogin"]]], jsii.get(self, "awsIamLogin"))

    @aws_iam_login.setter
    def aws_iam_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAwsIamLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53836afd9833676c20ec19f530b86324c6af5c9d6257d6b7dfdd14126ced9590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsIamLogin", value)

    @builtins.property
    @jsii.member(jsii_name="azureAdLogin")
    def azure_ad_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAzureAdLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAzureAdLogin"]]], jsii.get(self, "azureAdLogin"))

    @azure_ad_login.setter
    def azure_ad_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderAzureAdLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5dd8f0c398f158df4046a1a3a1bc3c87ff4e35e22f95d63a88a3c319570087a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureAdLogin", value)

    @builtins.property
    @jsii.member(jsii_name="certLogin")
    def cert_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderCertLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderCertLogin"]]], jsii.get(self, "certLogin"))

    @cert_login.setter
    def cert_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderCertLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a38080d2317b246a60aabcaa6b1f22bbe665d1ed787bdac02ff7816006f45806)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certLogin", value)

    @builtins.property
    @jsii.member(jsii_name="emailLogin")
    def email_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderEmailLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderEmailLogin"]]], jsii.get(self, "emailLogin"))

    @email_login.setter
    def email_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderEmailLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2446ac59e6db4d6239a06078083506b99754856fd50ed67ca521ed8a31c75949)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailLogin", value)

    @builtins.property
    @jsii.member(jsii_name="gcpLogin")
    def gcp_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderGcpLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderGcpLogin"]]], jsii.get(self, "gcpLogin"))

    @gcp_login.setter
    def gcp_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderGcpLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77068790da12ed2ef0be2680f852b814b91fe534d9a78eaec8f9f84751047101)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpLogin", value)

    @builtins.property
    @jsii.member(jsii_name="jwtLogin")
    def jwt_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderJwtLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderJwtLogin"]]], jsii.get(self, "jwtLogin"))

    @jwt_login.setter
    def jwt_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderJwtLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__193313b531b12af197212581b4fbd0d34ffffdb23190411ccc9215dde27ccea1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwtLogin", value)

    @builtins.property
    @jsii.member(jsii_name="tokenLogin")
    def token_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderTokenLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderTokenLogin"]]], jsii.get(self, "tokenLogin"))

    @token_login.setter
    def token_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderTokenLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d9326d685240cbd4aff2528b6c8d6fcea001884d8afec1cf5a7e2f9f0af5b23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenLogin", value)

    @builtins.property
    @jsii.member(jsii_name="uidLogin")
    def uid_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderUidLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderUidLogin"]]], jsii.get(self, "uidLogin"))

    @uid_login.setter
    def uid_login(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderUidLogin"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b0aa765befbf6d81bfc058046298a18870ffac8b4bbb5f7777defa482d2cc04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uidLogin", value)


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderApiKeyLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId", "access_key": "accessKey"},
)
class AkeylessProviderApiKeyLogin:
    def __init__(self, *, access_id: builtins.str, access_key: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.
        :param access_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_key AkeylessProvider#access_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ae342a9e1d3e21c82da9c9d8220d65337f652ae10677906efe546db1d500224)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument access_key", value=access_key, expected_type=type_hints["access_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
            "access_key": access_key,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_key AkeylessProvider#access_key}.'''
        result = self._values.get("access_key")
        assert result is not None, "Required property 'access_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderApiKeyLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderAwsIamLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId"},
)
class AkeylessProviderAwsIamLogin:
    def __init__(self, *, access_id: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__833f4ebf364e90a1ad61abdbdc9420ddabd94112a8b1efe00ed83d67db9e2d39)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderAwsIamLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderAzureAdLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId"},
)
class AkeylessProviderAzureAdLogin:
    def __init__(self, *, access_id: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ede3c8c76fb9f9060ef7b6011526cd50dbc0640d0f6b5a8e0ec2d92bcb0c99de)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderAzureAdLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderCertLogin",
    jsii_struct_bases=[],
    name_mapping={
        "access_id": "accessId",
        "cert_data": "certData",
        "cert_file_name": "certFileName",
        "key_data": "keyData",
        "key_file_name": "keyFileName",
    },
)
class AkeylessProviderCertLogin:
    def __init__(
        self,
        *,
        access_id: builtins.str,
        cert_data: typing.Optional[builtins.str] = None,
        cert_file_name: typing.Optional[builtins.str] = None,
        key_data: typing.Optional[builtins.str] = None,
        key_file_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.
        :param cert_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#cert_data AkeylessProvider#cert_data}.
        :param cert_file_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#cert_file_name AkeylessProvider#cert_file_name}.
        :param key_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#key_data AkeylessProvider#key_data}.
        :param key_file_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#key_file_name AkeylessProvider#key_file_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ddbef9982b88e01946c7e5770863758b9664b81936f1fdd6966706fa16248dc)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument cert_data", value=cert_data, expected_type=type_hints["cert_data"])
            check_type(argname="argument cert_file_name", value=cert_file_name, expected_type=type_hints["cert_file_name"])
            check_type(argname="argument key_data", value=key_data, expected_type=type_hints["key_data"])
            check_type(argname="argument key_file_name", value=key_file_name, expected_type=type_hints["key_file_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
        }
        if cert_data is not None:
            self._values["cert_data"] = cert_data
        if cert_file_name is not None:
            self._values["cert_file_name"] = cert_file_name
        if key_data is not None:
            self._values["key_data"] = key_data
        if key_file_name is not None:
            self._values["key_file_name"] = key_file_name

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cert_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#cert_data AkeylessProvider#cert_data}.'''
        result = self._values.get("cert_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_file_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#cert_file_name AkeylessProvider#cert_file_name}.'''
        result = self._values.get("cert_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#key_data AkeylessProvider#key_data}.'''
        result = self._values.get("key_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_file_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#key_file_name AkeylessProvider#key_file_name}.'''
        result = self._values.get("key_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderCertLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "api_gateway_address": "apiGatewayAddress",
        "api_key_login": "apiKeyLogin",
        "aws_iam_login": "awsIamLogin",
        "azure_ad_login": "azureAdLogin",
        "cert_login": "certLogin",
        "email_login": "emailLogin",
        "gcp_login": "gcpLogin",
        "jwt_login": "jwtLogin",
        "token_login": "tokenLogin",
        "uid_login": "uidLogin",
    },
)
class AkeylessProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        api_gateway_address: typing.Optional[builtins.str] = None,
        api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderApiKeyLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderAwsIamLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderAzureAdLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderCertLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderEmailLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderGcpLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderJwtLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        token_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderTokenLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AkeylessProviderUidLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#alias AkeylessProvider#alias}
        :param api_gateway_address: Origin URL of the API Gateway server. This is a URL with a scheme, a hostname and a port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#api_gateway_address AkeylessProvider#api_gateway_address}
        :param api_key_login: api_key_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#api_key_login AkeylessProvider#api_key_login}
        :param aws_iam_login: aws_iam_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#aws_iam_login AkeylessProvider#aws_iam_login}
        :param azure_ad_login: azure_ad_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#azure_ad_login AkeylessProvider#azure_ad_login}
        :param cert_login: cert_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#cert_login AkeylessProvider#cert_login}
        :param email_login: email_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#email_login AkeylessProvider#email_login}
        :param gcp_login: gcp_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#gcp_login AkeylessProvider#gcp_login}
        :param jwt_login: jwt_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#jwt_login AkeylessProvider#jwt_login}
        :param token_login: token_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#token_login AkeylessProvider#token_login}
        :param uid_login: uid_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#uid_login AkeylessProvider#uid_login}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c80218a6cf187a792438c44f7bea96c5d404c36ff3311194e3b916b221d615a0)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument api_gateway_address", value=api_gateway_address, expected_type=type_hints["api_gateway_address"])
            check_type(argname="argument api_key_login", value=api_key_login, expected_type=type_hints["api_key_login"])
            check_type(argname="argument aws_iam_login", value=aws_iam_login, expected_type=type_hints["aws_iam_login"])
            check_type(argname="argument azure_ad_login", value=azure_ad_login, expected_type=type_hints["azure_ad_login"])
            check_type(argname="argument cert_login", value=cert_login, expected_type=type_hints["cert_login"])
            check_type(argname="argument email_login", value=email_login, expected_type=type_hints["email_login"])
            check_type(argname="argument gcp_login", value=gcp_login, expected_type=type_hints["gcp_login"])
            check_type(argname="argument jwt_login", value=jwt_login, expected_type=type_hints["jwt_login"])
            check_type(argname="argument token_login", value=token_login, expected_type=type_hints["token_login"])
            check_type(argname="argument uid_login", value=uid_login, expected_type=type_hints["uid_login"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if api_gateway_address is not None:
            self._values["api_gateway_address"] = api_gateway_address
        if api_key_login is not None:
            self._values["api_key_login"] = api_key_login
        if aws_iam_login is not None:
            self._values["aws_iam_login"] = aws_iam_login
        if azure_ad_login is not None:
            self._values["azure_ad_login"] = azure_ad_login
        if cert_login is not None:
            self._values["cert_login"] = cert_login
        if email_login is not None:
            self._values["email_login"] = email_login
        if gcp_login is not None:
            self._values["gcp_login"] = gcp_login
        if jwt_login is not None:
            self._values["jwt_login"] = jwt_login
        if token_login is not None:
            self._values["token_login"] = token_login
        if uid_login is not None:
            self._values["uid_login"] = uid_login

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#alias AkeylessProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_gateway_address(self) -> typing.Optional[builtins.str]:
        '''Origin URL of the API Gateway server. This is a URL with a scheme, a hostname and a port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#api_gateway_address AkeylessProvider#api_gateway_address}
        '''
        result = self._values.get("api_gateway_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderApiKeyLogin]]]:
        '''api_key_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#api_key_login AkeylessProvider#api_key_login}
        '''
        result = self._values.get("api_key_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderApiKeyLogin]]], result)

    @builtins.property
    def aws_iam_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderAwsIamLogin]]]:
        '''aws_iam_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#aws_iam_login AkeylessProvider#aws_iam_login}
        '''
        result = self._values.get("aws_iam_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderAwsIamLogin]]], result)

    @builtins.property
    def azure_ad_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderAzureAdLogin]]]:
        '''azure_ad_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#azure_ad_login AkeylessProvider#azure_ad_login}
        '''
        result = self._values.get("azure_ad_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderAzureAdLogin]]], result)

    @builtins.property
    def cert_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderCertLogin]]]:
        '''cert_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#cert_login AkeylessProvider#cert_login}
        '''
        result = self._values.get("cert_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderCertLogin]]], result)

    @builtins.property
    def email_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderEmailLogin"]]]:
        '''email_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#email_login AkeylessProvider#email_login}
        '''
        result = self._values.get("email_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderEmailLogin"]]], result)

    @builtins.property
    def gcp_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderGcpLogin"]]]:
        '''gcp_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#gcp_login AkeylessProvider#gcp_login}
        '''
        result = self._values.get("gcp_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderGcpLogin"]]], result)

    @builtins.property
    def jwt_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderJwtLogin"]]]:
        '''jwt_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#jwt_login AkeylessProvider#jwt_login}
        '''
        result = self._values.get("jwt_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderJwtLogin"]]], result)

    @builtins.property
    def token_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderTokenLogin"]]]:
        '''token_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#token_login AkeylessProvider#token_login}
        '''
        result = self._values.get("token_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderTokenLogin"]]], result)

    @builtins.property
    def uid_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderUidLogin"]]]:
        '''uid_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#uid_login AkeylessProvider#uid_login}
        '''
        result = self._values.get("uid_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AkeylessProviderUidLogin"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderEmailLogin",
    jsii_struct_bases=[],
    name_mapping={"admin_email": "adminEmail", "admin_password": "adminPassword"},
)
class AkeylessProviderEmailLogin:
    def __init__(
        self,
        *,
        admin_email: builtins.str,
        admin_password: builtins.str,
    ) -> None:
        '''
        :param admin_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#admin_email AkeylessProvider#admin_email}.
        :param admin_password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#admin_password AkeylessProvider#admin_password}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ee39fd5c2ba5ace68a7b55e589aa0517e2eb5aae1daa509b066ea75ae8dc9c4)
            check_type(argname="argument admin_email", value=admin_email, expected_type=type_hints["admin_email"])
            check_type(argname="argument admin_password", value=admin_password, expected_type=type_hints["admin_password"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "admin_email": admin_email,
            "admin_password": admin_password,
        }

    @builtins.property
    def admin_email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#admin_email AkeylessProvider#admin_email}.'''
        result = self._values.get("admin_email")
        assert result is not None, "Required property 'admin_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#admin_password AkeylessProvider#admin_password}.'''
        result = self._values.get("admin_password")
        assert result is not None, "Required property 'admin_password' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderEmailLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderGcpLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId", "audience": "audience"},
)
class AkeylessProviderGcpLogin:
    def __init__(
        self,
        *,
        access_id: builtins.str,
        audience: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.
        :param audience: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#audience AkeylessProvider#audience}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f17b427804a3fc8c99419e3f64bed9d6982e3f72fee78e6a217dffb60be97ee2)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
        }
        if audience is not None:
            self._values["audience"] = audience

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#audience AkeylessProvider#audience}.'''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderGcpLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderJwtLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId", "jwt": "jwt"},
)
class AkeylessProviderJwtLogin:
    def __init__(self, *, access_id: builtins.str, jwt: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.
        :param jwt: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#jwt AkeylessProvider#jwt}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ac07c08d039d4697d3c41185c5831e9eee4b399f24bafc72e6f87b6cb57f696)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
            "jwt": jwt,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def jwt(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#jwt AkeylessProvider#jwt}.'''
        result = self._values.get("jwt")
        assert result is not None, "Required property 'jwt' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderJwtLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderTokenLogin",
    jsii_struct_bases=[],
    name_mapping={"token": "token"},
)
class AkeylessProviderTokenLogin:
    def __init__(self, *, token: builtins.str) -> None:
        '''
        :param token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#token AkeylessProvider#token}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58bafc5f980ab4ecfc77b03e452289f581f9d2b799fb4ea2c0ef7117118b40ed)
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "token": token,
        }

    @builtins.property
    def token(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#token AkeylessProvider#token}.'''
        result = self._values.get("token")
        assert result is not None, "Required property 'token' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderTokenLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.provider.AkeylessProviderUidLogin",
    jsii_struct_bases=[],
    name_mapping={"uid_token": "uidToken", "access_id": "accessId"},
)
class AkeylessProviderUidLogin:
    def __init__(
        self,
        *,
        uid_token: builtins.str,
        access_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param uid_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#uid_token AkeylessProvider#uid_token}.
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98734c340230bc430c5f4ae41120b42ee344ebe1cd3dc628d7aa5bda28054978)
            check_type(argname="argument uid_token", value=uid_token, expected_type=type_hints["uid_token"])
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "uid_token": uid_token,
        }
        if access_id is not None:
            self._values["access_id"] = access_id

    @builtins.property
    def uid_token(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#uid_token AkeylessProvider#uid_token}.'''
        result = self._values.get("uid_token")
        assert result is not None, "Required property 'uid_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs#access_id AkeylessProvider#access_id}.'''
        result = self._values.get("access_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AkeylessProviderUidLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AkeylessProvider",
    "AkeylessProviderApiKeyLogin",
    "AkeylessProviderAwsIamLogin",
    "AkeylessProviderAzureAdLogin",
    "AkeylessProviderCertLogin",
    "AkeylessProviderConfig",
    "AkeylessProviderEmailLogin",
    "AkeylessProviderGcpLogin",
    "AkeylessProviderJwtLogin",
    "AkeylessProviderTokenLogin",
    "AkeylessProviderUidLogin",
]

publication.publish()

def _typecheckingstub__8240bb7e189c60a5103b8e54843e452d0c83f7633d1c8a792f0d65a9b3b45e22(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias: typing.Optional[builtins.str] = None,
    api_gateway_address: typing.Optional[builtins.str] = None,
    api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderApiKeyLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderAwsIamLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderAzureAdLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderCertLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderEmailLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderGcpLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderJwtLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    token_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderTokenLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderUidLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b947e5ea64dd00e53a3fde6bb400724bff69aaf6f908f3064b7908704e489e40(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e81779c21704bf2442180c0cec8a8c32de6f42c7d3b864e5e0a436a41d2f0a72(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a42f2358ae72aa39a9ffeeb5b42816c13dd91dcfb46e3e847f8b67cffcbfb08e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20e32050dbaf6cf3b3b6f47c39a8661b65b63ea9978f108f35a1ea91828ee730(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderApiKeyLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53836afd9833676c20ec19f530b86324c6af5c9d6257d6b7dfdd14126ced9590(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderAwsIamLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5dd8f0c398f158df4046a1a3a1bc3c87ff4e35e22f95d63a88a3c319570087a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderAzureAdLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a38080d2317b246a60aabcaa6b1f22bbe665d1ed787bdac02ff7816006f45806(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderCertLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2446ac59e6db4d6239a06078083506b99754856fd50ed67ca521ed8a31c75949(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderEmailLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77068790da12ed2ef0be2680f852b814b91fe534d9a78eaec8f9f84751047101(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderGcpLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__193313b531b12af197212581b4fbd0d34ffffdb23190411ccc9215dde27ccea1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderJwtLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d9326d685240cbd4aff2528b6c8d6fcea001884d8afec1cf5a7e2f9f0af5b23(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderTokenLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b0aa765befbf6d81bfc058046298a18870ffac8b4bbb5f7777defa482d2cc04(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AkeylessProviderUidLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ae342a9e1d3e21c82da9c9d8220d65337f652ae10677906efe546db1d500224(
    *,
    access_id: builtins.str,
    access_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__833f4ebf364e90a1ad61abdbdc9420ddabd94112a8b1efe00ed83d67db9e2d39(
    *,
    access_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ede3c8c76fb9f9060ef7b6011526cd50dbc0640d0f6b5a8e0ec2d92bcb0c99de(
    *,
    access_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ddbef9982b88e01946c7e5770863758b9664b81936f1fdd6966706fa16248dc(
    *,
    access_id: builtins.str,
    cert_data: typing.Optional[builtins.str] = None,
    cert_file_name: typing.Optional[builtins.str] = None,
    key_data: typing.Optional[builtins.str] = None,
    key_file_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c80218a6cf187a792438c44f7bea96c5d404c36ff3311194e3b916b221d615a0(
    *,
    alias: typing.Optional[builtins.str] = None,
    api_gateway_address: typing.Optional[builtins.str] = None,
    api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderApiKeyLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderAwsIamLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderAzureAdLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderCertLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderEmailLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderGcpLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderJwtLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    token_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderTokenLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AkeylessProviderUidLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ee39fd5c2ba5ace68a7b55e589aa0517e2eb5aae1daa509b066ea75ae8dc9c4(
    *,
    admin_email: builtins.str,
    admin_password: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f17b427804a3fc8c99419e3f64bed9d6982e3f72fee78e6a217dffb60be97ee2(
    *,
    access_id: builtins.str,
    audience: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ac07c08d039d4697d3c41185c5831e9eee4b399f24bafc72e6f87b6cb57f696(
    *,
    access_id: builtins.str,
    jwt: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58bafc5f980ab4ecfc77b03e452289f581f9d2b799fb4ea2c0ef7117118b40ed(
    *,
    token: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98734c340230bc430c5f4ae41120b42ee344ebe1cd3dc628d7aa5bda28054978(
    *,
    uid_token: builtins.str,
    access_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
