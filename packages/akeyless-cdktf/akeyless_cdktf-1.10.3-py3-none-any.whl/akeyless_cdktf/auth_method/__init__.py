'''
# `akeyless_auth_method`

Refer to the Terraform Registry for docs: [`akeyless_auth_method`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method).
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


class AuthMethod(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethod",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method akeyless_auth_method}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        path: builtins.str,
        access_expires: typing.Optional[jsii.Number] = None,
        api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_iam: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodAwsIam", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_ad: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodAzureAd", typing.Dict[builtins.str, typing.Any]]]]] = None,
        bound_ips: typing.Optional[builtins.str] = None,
        gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodGcp", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        saml: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodSaml", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method akeyless_auth_method} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param path: The path where the Auth Method will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#path AuthMethod#path}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#access_expires AuthMethod#access_expires}
        :param api_key: api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#api_key AuthMethod#api_key}
        :param aws_iam: aws_iam block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#aws_iam AuthMethod#aws_iam}
        :param azure_ad: azure_ad block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#azure_ad AuthMethod#azure_ad}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_ips AuthMethod#bound_ips}
        :param gcp: gcp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#gcp AuthMethod#gcp}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#id AuthMethod#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param saml: saml block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#saml AuthMethod#saml}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d1e97e9cc9decab009d97d74f1a8e1ef2a005005f3e6693d416908d64f60bd8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AuthMethodConfig(
            path=path,
            access_expires=access_expires,
            api_key=api_key,
            aws_iam=aws_iam,
            azure_ad=azure_ad,
            bound_ips=bound_ips,
            gcp=gcp,
            id=id,
            saml=saml,
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
        '''Generates CDKTF code for importing a AuthMethod resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AuthMethod to import.
        :param import_from_id: The id of the existing AuthMethod that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AuthMethod to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0dbb0775477ff984b18a7ea1feff0a1508a99da8f3d36911b90e4b7ee63995f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putApiKey")
    def put_api_key(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodApiKey", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2ece26020829f0c964d1da742edf6d9f7b39bc427a89a47396e9870f5d8b20e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKey", [value]))

    @jsii.member(jsii_name="putAwsIam")
    def put_aws_iam(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodAwsIam", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4be1997c14b598b9fb5664a335789fabc9766cf531429987c5b1b3a2530c5c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAwsIam", [value]))

    @jsii.member(jsii_name="putAzureAd")
    def put_azure_ad(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodAzureAd", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b80130d7419041e02a7d1cf7dcb07a07cf1a07a4e9bec5e470c2524d8333690)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAzureAd", [value]))

    @jsii.member(jsii_name="putGcp")
    def put_gcp(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodGcp", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6607127be3d109d4b7a7965c0541e3c8c0bb5a3b92aa630af7535265ed649e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGcp", [value]))

    @jsii.member(jsii_name="putSaml")
    def put_saml(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodSaml", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15c7f85414a25a40a7919baf276dc324fe83966d3e7363ddd5efadf21da005a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSaml", [value]))

    @jsii.member(jsii_name="resetAccessExpires")
    def reset_access_expires(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessExpires", []))

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetAwsIam")
    def reset_aws_iam(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsIam", []))

    @jsii.member(jsii_name="resetAzureAd")
    def reset_azure_ad(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureAd", []))

    @jsii.member(jsii_name="resetBoundIps")
    def reset_bound_ips(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundIps", []))

    @jsii.member(jsii_name="resetGcp")
    def reset_gcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcp", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSaml")
    def reset_saml(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSaml", []))

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
    @jsii.member(jsii_name="accessKey")
    def access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKey"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> "AuthMethodApiKeyList":
        return typing.cast("AuthMethodApiKeyList", jsii.get(self, "apiKey"))

    @builtins.property
    @jsii.member(jsii_name="awsIam")
    def aws_iam(self) -> "AuthMethodAwsIamList":
        return typing.cast("AuthMethodAwsIamList", jsii.get(self, "awsIam"))

    @builtins.property
    @jsii.member(jsii_name="azureAd")
    def azure_ad(self) -> "AuthMethodAzureAdList":
        return typing.cast("AuthMethodAzureAdList", jsii.get(self, "azureAd"))

    @builtins.property
    @jsii.member(jsii_name="gcp")
    def gcp(self) -> "AuthMethodGcpList":
        return typing.cast("AuthMethodGcpList", jsii.get(self, "gcp"))

    @builtins.property
    @jsii.member(jsii_name="saml")
    def saml(self) -> "AuthMethodSamlList":
        return typing.cast("AuthMethodSamlList", jsii.get(self, "saml"))

    @builtins.property
    @jsii.member(jsii_name="accessExpiresInput")
    def access_expires_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "accessExpiresInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodApiKey"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodApiKey"]]], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="awsIamInput")
    def aws_iam_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodAwsIam"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodAwsIam"]]], jsii.get(self, "awsIamInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdInput")
    def azure_ad_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodAzureAd"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodAzureAd"]]], jsii.get(self, "azureAdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundIpsInput")
    def bound_ips_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "boundIpsInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpInput")
    def gcp_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcp"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcp"]]], jsii.get(self, "gcpInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="samlInput")
    def saml_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodSaml"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodSaml"]]], jsii.get(self, "samlInput"))

    @builtins.property
    @jsii.member(jsii_name="accessExpires")
    def access_expires(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "accessExpires"))

    @access_expires.setter
    def access_expires(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__432e4e495fc76a8b16c2b98a60ec0f91d5cf0caf18bb2a62f7eea3967a03aab4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessExpires", value)

    @builtins.property
    @jsii.member(jsii_name="boundIps")
    def bound_ips(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "boundIps"))

    @bound_ips.setter
    def bound_ips(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__028f1c58aa86c2999103d1d0933b16d949e8d0429f8dfd74a0c0d4a7517d53b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundIps", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfe2af6cd6aa1b4db4b76f4987ea363da41f4f0ee521a9e0607ab2005b66818d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab0ee09496e87161447b1c5d3d64257f8c45350fa7eee9dcb8b1da7d14eb0192)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value)


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodApiKey",
    jsii_struct_bases=[],
    name_mapping={},
)
class AuthMethodApiKey:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthMethodApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodApiKeyList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fab80f5317e2563abef8e83f80c9f7a8af6ebe6d5aba99e03e8c6c4bdbe1578a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AuthMethodApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fcbc6ac897ad0e0597bff2ab7db290d30230d452ac7f09df0e43afcde930dc7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthMethodApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f2c0bab3d1bad583236723ddf05653a11deb4fe5d94ab20935a520bbb4e1515)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ca64cda6e295525754b07375194e7605fc40e6c18ef5b4b82d87c8d2d80209b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__912c973247e6da2acd8989073bdebf235a31a922437ac2aa6a173baee389a3dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodApiKey]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodApiKey]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16fbfe460dc76a74ddf4bb8a5e4242821fdb945b186b94e4337fcf6561ff972d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodApiKeyOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21c20a10f8519728e9232a11c55207e7733bfdc4798fad77039a5409f727a001)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[AuthMethodApiKey, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[AuthMethodApiKey, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[AuthMethodApiKey, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__617df0d4a1b9940dc8dc28f79a41cb0759877b7f4ddf411e7631369d2fb51303)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodAwsIam",
    jsii_struct_bases=[],
    name_mapping={
        "bound_aws_account_id": "boundAwsAccountId",
        "bound_arn": "boundArn",
        "bound_resource_id": "boundResourceId",
        "bound_role_id": "boundRoleId",
        "bound_role_name": "boundRoleName",
        "bound_user_id": "boundUserId",
        "bound_user_name": "boundUserName",
        "sts_url": "stsUrl",
    },
)
class AuthMethodAwsIam:
    def __init__(
        self,
        *,
        bound_aws_account_id: typing.Sequence[builtins.str],
        bound_arn: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_role_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_role_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_user_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_user_name: typing.Optional[typing.Sequence[builtins.str]] = None,
        sts_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bound_aws_account_id: A list of AWS account-IDs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_aws_account_id AuthMethod#bound_aws_account_id}
        :param bound_arn: A list of full arns that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_arn AuthMethod#bound_arn}
        :param bound_resource_id: A list of full resource ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_id AuthMethod#bound_resource_id}
        :param bound_role_id: A list of full role ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_role_id AuthMethod#bound_role_id}
        :param bound_role_name: A list of full role-name that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_role_name AuthMethod#bound_role_name}
        :param bound_user_id: A list of full user ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_user_id AuthMethod#bound_user_id}
        :param bound_user_name: A list of full user-name that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_user_name AuthMethod#bound_user_name}
        :param sts_url: STS URL (default: https://sts.amazonaws.com). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#sts_url AuthMethod#sts_url}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de6152d37409e8f6a71100fc9efe37940c4f828613ad0935f3773e0ff56b058c)
            check_type(argname="argument bound_aws_account_id", value=bound_aws_account_id, expected_type=type_hints["bound_aws_account_id"])
            check_type(argname="argument bound_arn", value=bound_arn, expected_type=type_hints["bound_arn"])
            check_type(argname="argument bound_resource_id", value=bound_resource_id, expected_type=type_hints["bound_resource_id"])
            check_type(argname="argument bound_role_id", value=bound_role_id, expected_type=type_hints["bound_role_id"])
            check_type(argname="argument bound_role_name", value=bound_role_name, expected_type=type_hints["bound_role_name"])
            check_type(argname="argument bound_user_id", value=bound_user_id, expected_type=type_hints["bound_user_id"])
            check_type(argname="argument bound_user_name", value=bound_user_name, expected_type=type_hints["bound_user_name"])
            check_type(argname="argument sts_url", value=sts_url, expected_type=type_hints["sts_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bound_aws_account_id": bound_aws_account_id,
        }
        if bound_arn is not None:
            self._values["bound_arn"] = bound_arn
        if bound_resource_id is not None:
            self._values["bound_resource_id"] = bound_resource_id
        if bound_role_id is not None:
            self._values["bound_role_id"] = bound_role_id
        if bound_role_name is not None:
            self._values["bound_role_name"] = bound_role_name
        if bound_user_id is not None:
            self._values["bound_user_id"] = bound_user_id
        if bound_user_name is not None:
            self._values["bound_user_name"] = bound_user_name
        if sts_url is not None:
            self._values["sts_url"] = sts_url

    @builtins.property
    def bound_aws_account_id(self) -> typing.List[builtins.str]:
        '''A list of AWS account-IDs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_aws_account_id AuthMethod#bound_aws_account_id}
        '''
        result = self._values.get("bound_aws_account_id")
        assert result is not None, "Required property 'bound_aws_account_id' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def bound_arn(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full arns that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_arn AuthMethod#bound_arn}
        '''
        result = self._values.get("bound_arn")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full resource ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_id AuthMethod#bound_resource_id}
        '''
        result = self._values.get("bound_resource_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_role_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full role ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_role_id AuthMethod#bound_role_id}
        '''
        result = self._values.get("bound_role_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_role_name(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full role-name that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_role_name AuthMethod#bound_role_name}
        '''
        result = self._values.get("bound_role_name")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_user_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full user ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_user_id AuthMethod#bound_user_id}
        '''
        result = self._values.get("bound_user_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_user_name(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full user-name that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_user_name AuthMethod#bound_user_name}
        '''
        result = self._values.get("bound_user_name")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def sts_url(self) -> typing.Optional[builtins.str]:
        '''STS URL (default: https://sts.amazonaws.com).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#sts_url AuthMethod#sts_url}
        '''
        result = self._values.get("sts_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodAwsIam(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthMethodAwsIamList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodAwsIamList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df6d29154280c28778b431fa4b238183a2d23e28e0691ed7163a61920c5153d0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AuthMethodAwsIamOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7be0a2dfcbe8f5dfbff320a82984339c9328acba22cbbbe0566d54775555784)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthMethodAwsIamOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd1fc76efe14eafdc34ad6714d8127f0489636fa4176ce97bfe261edaf599349)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c280d5addca4fba551748189744af24eb4e1a9e12954abf6e3ef57fa0309bc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39f974e82641e5d53d99657fb8e81439385b65c86377f6be1e1daf7c5554d0cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAwsIam]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAwsIam]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAwsIam]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8822250633560b4e35f0eef9c9da56ac08c7cbd10a611f3b7ab0d232fb883b3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodAwsIamOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodAwsIamOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebe66538d198e9ab4dd8f0d6dd26b1923f007d9a3ba897d324a0b6c3c2d26ea4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBoundArn")
    def reset_bound_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundArn", []))

    @jsii.member(jsii_name="resetBoundResourceId")
    def reset_bound_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceId", []))

    @jsii.member(jsii_name="resetBoundRoleId")
    def reset_bound_role_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundRoleId", []))

    @jsii.member(jsii_name="resetBoundRoleName")
    def reset_bound_role_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundRoleName", []))

    @jsii.member(jsii_name="resetBoundUserId")
    def reset_bound_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundUserId", []))

    @jsii.member(jsii_name="resetBoundUserName")
    def reset_bound_user_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundUserName", []))

    @jsii.member(jsii_name="resetStsUrl")
    def reset_sts_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStsUrl", []))

    @builtins.property
    @jsii.member(jsii_name="boundArnInput")
    def bound_arn_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundArnInput"))

    @builtins.property
    @jsii.member(jsii_name="boundAwsAccountIdInput")
    def bound_aws_account_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundAwsAccountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceIdInput")
    def bound_resource_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundRoleIdInput")
    def bound_role_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundRoleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundRoleNameInput")
    def bound_role_name_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundRoleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="boundUserIdInput")
    def bound_user_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundUserIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundUserNameInput")
    def bound_user_name_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundUserNameInput"))

    @builtins.property
    @jsii.member(jsii_name="stsUrlInput")
    def sts_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stsUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="boundArn")
    def bound_arn(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundArn"))

    @bound_arn.setter
    def bound_arn(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__831756db896ce5bd9474aae18e8747dc0c0ef38826902fd895535ab4ce453330)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundArn", value)

    @builtins.property
    @jsii.member(jsii_name="boundAwsAccountId")
    def bound_aws_account_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundAwsAccountId"))

    @bound_aws_account_id.setter
    def bound_aws_account_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c95771696aaf2960637e19920812be301cad1eb288ca2c18352072b3f544c286)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundAwsAccountId", value)

    @builtins.property
    @jsii.member(jsii_name="boundResourceId")
    def bound_resource_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceId"))

    @bound_resource_id.setter
    def bound_resource_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1f2f1eae6102e97f4bb6b988f9bd67e0f6a74ae39c7aba52893c40836909ddb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceId", value)

    @builtins.property
    @jsii.member(jsii_name="boundRoleId")
    def bound_role_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundRoleId"))

    @bound_role_id.setter
    def bound_role_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__469700b1194a5d669d85ceacf010a744b8b3cb93533d4f691cbd98c4b5b68f83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundRoleId", value)

    @builtins.property
    @jsii.member(jsii_name="boundRoleName")
    def bound_role_name(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundRoleName"))

    @bound_role_name.setter
    def bound_role_name(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74d397383d8c67e20dbfe0aa5892c1d34d1155831a6796cfde8a9503ed45d9ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundRoleName", value)

    @builtins.property
    @jsii.member(jsii_name="boundUserId")
    def bound_user_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundUserId"))

    @bound_user_id.setter
    def bound_user_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__914f96af21c6ef77b057bc8d8309cc3719d34dd9dbba0468600407b00d15c82c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundUserId", value)

    @builtins.property
    @jsii.member(jsii_name="boundUserName")
    def bound_user_name(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundUserName"))

    @bound_user_name.setter
    def bound_user_name(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55bda56dac231dba92461bb7810366d1663c6e545859c7d5c8cb7675ca3de19b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundUserName", value)

    @builtins.property
    @jsii.member(jsii_name="stsUrl")
    def sts_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stsUrl"))

    @sts_url.setter
    def sts_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c064d59dda42a7e995f5f9f4e989351edea1351bc331eee8859a1b1a51a908b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stsUrl", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAwsIam]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAwsIam]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAwsIam]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7080fba3b71ae7e04ae871c950812483d3bf75a1465d514cc74388c56a70fa16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodAzureAd",
    jsii_struct_bases=[],
    name_mapping={
        "bound_tenant_id": "boundTenantId",
        "bound_group_id": "boundGroupId",
        "bound_providers": "boundProviders",
        "bound_resource_id": "boundResourceId",
        "bound_resource_names": "boundResourceNames",
        "bound_resource_types": "boundResourceTypes",
        "bound_rg_id": "boundRgId",
        "bound_spid": "boundSpid",
        "bound_sub_id": "boundSubId",
        "custom_audience": "customAudience",
        "custom_issuer": "customIssuer",
        "jwks_uri": "jwksUri",
    },
)
class AuthMethodAzureAd:
    def __init__(
        self,
        *,
        bound_tenant_id: builtins.str,
        bound_group_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_rg_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_spid: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_sub_id: typing.Optional[typing.Sequence[builtins.str]] = None,
        custom_audience: typing.Optional[builtins.str] = None,
        custom_issuer: typing.Optional[builtins.str] = None,
        jwks_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bound_tenant_id: The Azure tenant id that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_tenant_id AuthMethod#bound_tenant_id}
        :param bound_group_id: A list of group ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_group_id AuthMethod#bound_group_id}
        :param bound_providers: A list of resource providers that the access is restricted to (e.g, Microsoft.Compute, Microsoft.ManagedIdentity, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_providers AuthMethod#bound_providers}
        :param bound_resource_id: A list of full resource ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_id AuthMethod#bound_resource_id}
        :param bound_resource_names: A list of resource names that the access is restricted to (e.g, a virtual machine name, scale set name, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_names AuthMethod#bound_resource_names}
        :param bound_resource_types: A list of resource types that the access is restricted to (e.g, virtualMachines, userAssignedIdentities, etc). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_types AuthMethod#bound_resource_types}
        :param bound_rg_id: A list of resource groups that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_rg_id AuthMethod#bound_rg_id}
        :param bound_spid: A list of service principal IDs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_spid AuthMethod#bound_spid}
        :param bound_sub_id: A list of subscription ids that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_sub_id AuthMethod#bound_sub_id}
        :param custom_audience: The audience in the JWT. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#custom_audience AuthMethod#custom_audience}
        :param custom_issuer: Issuer URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#custom_issuer AuthMethod#custom_issuer}
        :param jwks_uri: The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#jwks_uri AuthMethod#jwks_uri}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c34d71caa10a23b05ad45d73a5372e6601d76c4b1a543a5453db225d6d8fc2d9)
            check_type(argname="argument bound_tenant_id", value=bound_tenant_id, expected_type=type_hints["bound_tenant_id"])
            check_type(argname="argument bound_group_id", value=bound_group_id, expected_type=type_hints["bound_group_id"])
            check_type(argname="argument bound_providers", value=bound_providers, expected_type=type_hints["bound_providers"])
            check_type(argname="argument bound_resource_id", value=bound_resource_id, expected_type=type_hints["bound_resource_id"])
            check_type(argname="argument bound_resource_names", value=bound_resource_names, expected_type=type_hints["bound_resource_names"])
            check_type(argname="argument bound_resource_types", value=bound_resource_types, expected_type=type_hints["bound_resource_types"])
            check_type(argname="argument bound_rg_id", value=bound_rg_id, expected_type=type_hints["bound_rg_id"])
            check_type(argname="argument bound_spid", value=bound_spid, expected_type=type_hints["bound_spid"])
            check_type(argname="argument bound_sub_id", value=bound_sub_id, expected_type=type_hints["bound_sub_id"])
            check_type(argname="argument custom_audience", value=custom_audience, expected_type=type_hints["custom_audience"])
            check_type(argname="argument custom_issuer", value=custom_issuer, expected_type=type_hints["custom_issuer"])
            check_type(argname="argument jwks_uri", value=jwks_uri, expected_type=type_hints["jwks_uri"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "bound_tenant_id": bound_tenant_id,
        }
        if bound_group_id is not None:
            self._values["bound_group_id"] = bound_group_id
        if bound_providers is not None:
            self._values["bound_providers"] = bound_providers
        if bound_resource_id is not None:
            self._values["bound_resource_id"] = bound_resource_id
        if bound_resource_names is not None:
            self._values["bound_resource_names"] = bound_resource_names
        if bound_resource_types is not None:
            self._values["bound_resource_types"] = bound_resource_types
        if bound_rg_id is not None:
            self._values["bound_rg_id"] = bound_rg_id
        if bound_spid is not None:
            self._values["bound_spid"] = bound_spid
        if bound_sub_id is not None:
            self._values["bound_sub_id"] = bound_sub_id
        if custom_audience is not None:
            self._values["custom_audience"] = custom_audience
        if custom_issuer is not None:
            self._values["custom_issuer"] = custom_issuer
        if jwks_uri is not None:
            self._values["jwks_uri"] = jwks_uri

    @builtins.property
    def bound_tenant_id(self) -> builtins.str:
        '''The Azure tenant id that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_tenant_id AuthMethod#bound_tenant_id}
        '''
        result = self._values.get("bound_tenant_id")
        assert result is not None, "Required property 'bound_tenant_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bound_group_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of group ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_group_id AuthMethod#bound_group_id}
        '''
        result = self._values.get("bound_group_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_providers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource providers that the access is restricted to (e.g, Microsoft.Compute, Microsoft.ManagedIdentity, etc).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_providers AuthMethod#bound_providers}
        '''
        result = self._values.get("bound_providers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of full resource ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_id AuthMethod#bound_resource_id}
        '''
        result = self._values.get("bound_resource_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource names that the access is restricted to (e.g, a virtual machine name, scale set name, etc).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_names AuthMethod#bound_resource_names}
        '''
        result = self._values.get("bound_resource_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_resource_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource types that the access is restricted to (e.g, virtualMachines, userAssignedIdentities, etc).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_resource_types AuthMethod#bound_resource_types}
        '''
        result = self._values.get("bound_resource_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_rg_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of resource groups that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_rg_id AuthMethod#bound_rg_id}
        '''
        result = self._values.get("bound_rg_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_spid(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of service principal IDs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_spid AuthMethod#bound_spid}
        '''
        result = self._values.get("bound_spid")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_sub_id(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of subscription ids that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_sub_id AuthMethod#bound_sub_id}
        '''
        result = self._values.get("bound_sub_id")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def custom_audience(self) -> typing.Optional[builtins.str]:
        '''The audience in the JWT.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#custom_audience AuthMethod#custom_audience}
        '''
        result = self._values.get("custom_audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_issuer(self) -> typing.Optional[builtins.str]:
        '''Issuer URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#custom_issuer AuthMethod#custom_issuer}
        '''
        result = self._values.get("custom_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwks_uri(self) -> typing.Optional[builtins.str]:
        '''The URL to the JSON Web Key Set (JWKS) that containing the public keys that should be used to verify any JSON Web Token (JWT) issued by the authorization server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#jwks_uri AuthMethod#jwks_uri}
        '''
        result = self._values.get("jwks_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodAzureAd(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthMethodAzureAdList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodAzureAdList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69c6d54c0bbd515d24d5995c26f53d2d9a5f1914b09bbf526989b0c352d11598)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AuthMethodAzureAdOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__690593bb2496b5485e629256eb94a59ca6b7d369878b92db717cac17ce9837b5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthMethodAzureAdOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64e3e8118260a9d94eae3a8817b66d44294e679d5c191a27d817db4aee2c600d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9e2ed3c302cd29d1a9173faa9feda059b31e55b96f3bb3b225de8297506c136)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b790ec5c09765b2659bea5f9f84933543bc9e7546fe17b88296604c6c60da334)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAzureAd]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAzureAd]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAzureAd]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc8f3a013376f30b9151e61ae2e296370e1192ac03b4b15c3c081e6282332ab7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodAzureAdOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodAzureAdOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85cfe8fbcb025d806bd79b3d5dc5b62e36a11a82a193e2e2d61af2387abf849d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBoundGroupId")
    def reset_bound_group_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundGroupId", []))

    @jsii.member(jsii_name="resetBoundProviders")
    def reset_bound_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundProviders", []))

    @jsii.member(jsii_name="resetBoundResourceId")
    def reset_bound_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceId", []))

    @jsii.member(jsii_name="resetBoundResourceNames")
    def reset_bound_resource_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceNames", []))

    @jsii.member(jsii_name="resetBoundResourceTypes")
    def reset_bound_resource_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundResourceTypes", []))

    @jsii.member(jsii_name="resetBoundRgId")
    def reset_bound_rg_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundRgId", []))

    @jsii.member(jsii_name="resetBoundSpid")
    def reset_bound_spid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundSpid", []))

    @jsii.member(jsii_name="resetBoundSubId")
    def reset_bound_sub_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundSubId", []))

    @jsii.member(jsii_name="resetCustomAudience")
    def reset_custom_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomAudience", []))

    @jsii.member(jsii_name="resetCustomIssuer")
    def reset_custom_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomIssuer", []))

    @jsii.member(jsii_name="resetJwksUri")
    def reset_jwks_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwksUri", []))

    @builtins.property
    @jsii.member(jsii_name="boundGroupIdInput")
    def bound_group_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundGroupIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundProvidersInput")
    def bound_providers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundProvidersInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceIdInput")
    def bound_resource_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceNamesInput")
    def bound_resource_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundResourceTypesInput")
    def bound_resource_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundResourceTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundRgIdInput")
    def bound_rg_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundRgIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundSpidInput")
    def bound_spid_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundSpidInput"))

    @builtins.property
    @jsii.member(jsii_name="boundSubIdInput")
    def bound_sub_id_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundSubIdInput"))

    @builtins.property
    @jsii.member(jsii_name="boundTenantIdInput")
    def bound_tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "boundTenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customAudienceInput")
    def custom_audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customAudienceInput"))

    @builtins.property
    @jsii.member(jsii_name="customIssuerInput")
    def custom_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="jwksUriInput")
    def jwks_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwksUriInput"))

    @builtins.property
    @jsii.member(jsii_name="boundGroupId")
    def bound_group_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundGroupId"))

    @bound_group_id.setter
    def bound_group_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a241a5b650b2103def926755e841fb776cba74516060c0a795b1d56b5d5dc2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundGroupId", value)

    @builtins.property
    @jsii.member(jsii_name="boundProviders")
    def bound_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundProviders"))

    @bound_providers.setter
    def bound_providers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67e788752789dc3ee80364636f17b2c2a100f9a668f026dbdeb2520ece10c952)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundProviders", value)

    @builtins.property
    @jsii.member(jsii_name="boundResourceId")
    def bound_resource_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceId"))

    @bound_resource_id.setter
    def bound_resource_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ad3419b4d695b551919568bca4d70c71a88ae9099258e8c17e735e249fbedc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceId", value)

    @builtins.property
    @jsii.member(jsii_name="boundResourceNames")
    def bound_resource_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceNames"))

    @bound_resource_names.setter
    def bound_resource_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44dc45b5d01128c4833305840915f2ef528790bb606d0f9e694e4a0a25fd138f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceNames", value)

    @builtins.property
    @jsii.member(jsii_name="boundResourceTypes")
    def bound_resource_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundResourceTypes"))

    @bound_resource_types.setter
    def bound_resource_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__707e9f3535c5c56bd12ca642082209cdc428085e896b7f5517b6df275796ad88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundResourceTypes", value)

    @builtins.property
    @jsii.member(jsii_name="boundRgId")
    def bound_rg_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundRgId"))

    @bound_rg_id.setter
    def bound_rg_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28fd9308171736a97d238a391c8d70e9fb69421bacbfaad5bdc4a69621ac2f5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundRgId", value)

    @builtins.property
    @jsii.member(jsii_name="boundSpid")
    def bound_spid(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundSpid"))

    @bound_spid.setter
    def bound_spid(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0999ca36cc7378a5e8c30f0c29000e15b542136af18c735b403eb876f032a18d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundSpid", value)

    @builtins.property
    @jsii.member(jsii_name="boundSubId")
    def bound_sub_id(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundSubId"))

    @bound_sub_id.setter
    def bound_sub_id(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0635aab420c793fe3543c7b34e4737d78c4cbc8898441a26f1445b53df70e5e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundSubId", value)

    @builtins.property
    @jsii.member(jsii_name="boundTenantId")
    def bound_tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "boundTenantId"))

    @bound_tenant_id.setter
    def bound_tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dabd3458b606b78de7636e806d7c5ebd0802a0638071d01ee0f76aafe02009af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundTenantId", value)

    @builtins.property
    @jsii.member(jsii_name="customAudience")
    def custom_audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customAudience"))

    @custom_audience.setter
    def custom_audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98f16ebdef1ea74ca028fc6156f8443711cd0cf4163556c7a93385da9ae9a1ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customAudience", value)

    @builtins.property
    @jsii.member(jsii_name="customIssuer")
    def custom_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customIssuer"))

    @custom_issuer.setter
    def custom_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9b6ba990e41220e3800d39bebd27bca68e33959700e96ae31772ae63e130f20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="jwksUri")
    def jwks_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwksUri"))

    @jwks_uri.setter
    def jwks_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cd5da5b5cce2fc3a5add87619a5b471540dd01409cd337e3037e9d457166495)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwksUri", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAzureAd]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAzureAd]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAzureAd]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9541747c3848edc4a4315256da656b1dae2a7d003a6f3b204e3698eabca57aa9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodConfig",
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
        "access_expires": "accessExpires",
        "api_key": "apiKey",
        "aws_iam": "awsIam",
        "azure_ad": "azureAd",
        "bound_ips": "boundIps",
        "gcp": "gcp",
        "id": "id",
        "saml": "saml",
    },
)
class AuthMethodConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_expires: typing.Optional[jsii.Number] = None,
        api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_iam: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAwsIam, typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_ad: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAzureAd, typing.Dict[builtins.str, typing.Any]]]]] = None,
        bound_ips: typing.Optional[builtins.str] = None,
        gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodGcp", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        saml: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodSaml", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param path: The path where the Auth Method will be stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#path AuthMethod#path}
        :param access_expires: Access expiration date in Unix timestamp (select 0 for access without expiry date). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#access_expires AuthMethod#access_expires}
        :param api_key: api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#api_key AuthMethod#api_key}
        :param aws_iam: aws_iam block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#aws_iam AuthMethod#aws_iam}
        :param azure_ad: azure_ad block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#azure_ad AuthMethod#azure_ad}
        :param bound_ips: A CIDR whitelist with the IPs that the access is restricted to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_ips AuthMethod#bound_ips}
        :param gcp: gcp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#gcp AuthMethod#gcp}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#id AuthMethod#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param saml: saml block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#saml AuthMethod#saml}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b180d7fe06451ef8d8caff42b4afea4cc77c5e3aaeee5b03ae7e19feb761a2a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument access_expires", value=access_expires, expected_type=type_hints["access_expires"])
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument aws_iam", value=aws_iam, expected_type=type_hints["aws_iam"])
            check_type(argname="argument azure_ad", value=azure_ad, expected_type=type_hints["azure_ad"])
            check_type(argname="argument bound_ips", value=bound_ips, expected_type=type_hints["bound_ips"])
            check_type(argname="argument gcp", value=gcp, expected_type=type_hints["gcp"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument saml", value=saml, expected_type=type_hints["saml"])
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
        if access_expires is not None:
            self._values["access_expires"] = access_expires
        if api_key is not None:
            self._values["api_key"] = api_key
        if aws_iam is not None:
            self._values["aws_iam"] = aws_iam
        if azure_ad is not None:
            self._values["azure_ad"] = azure_ad
        if bound_ips is not None:
            self._values["bound_ips"] = bound_ips
        if gcp is not None:
            self._values["gcp"] = gcp
        if id is not None:
            self._values["id"] = id
        if saml is not None:
            self._values["saml"] = saml

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
        '''The path where the Auth Method will be stored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#path AuthMethod#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_expires(self) -> typing.Optional[jsii.Number]:
        '''Access expiration date in Unix timestamp (select 0 for access without expiry date).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#access_expires AuthMethod#access_expires}
        '''
        result = self._values.get("access_expires")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def api_key(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodApiKey]]]:
        '''api_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#api_key AuthMethod#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodApiKey]]], result)

    @builtins.property
    def aws_iam(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAwsIam]]]:
        '''aws_iam block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#aws_iam AuthMethod#aws_iam}
        '''
        result = self._values.get("aws_iam")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAwsIam]]], result)

    @builtins.property
    def azure_ad(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAzureAd]]]:
        '''azure_ad block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#azure_ad AuthMethod#azure_ad}
        '''
        result = self._values.get("azure_ad")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAzureAd]]], result)

    @builtins.property
    def bound_ips(self) -> typing.Optional[builtins.str]:
        '''A CIDR whitelist with the IPs that the access is restricted to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_ips AuthMethod#bound_ips}
        '''
        result = self._values.get("bound_ips")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcp"]]]:
        '''gcp block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#gcp AuthMethod#gcp}
        '''
        result = self._values.get("gcp")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcp"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#id AuthMethod#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def saml(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodSaml"]]]:
        '''saml block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#saml AuthMethod#saml}
        '''
        result = self._values.get("saml")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodSaml"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodGcp",
    jsii_struct_bases=[],
    name_mapping={
        "service_account_creds_data": "serviceAccountCredsData",
        "audience": "audience",
        "gce": "gce",
        "iam": "iam",
    },
)
class AuthMethodGcp:
    def __init__(
        self,
        *,
        service_account_creds_data: builtins.str,
        audience: typing.Optional[builtins.str] = None,
        gce: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodGcpGce", typing.Dict[builtins.str, typing.Any]]]]] = None,
        iam: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AuthMethodGcpIam", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param service_account_creds_data: Service Account creds data, base64 encoded. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#service_account_creds_data AuthMethod#service_account_creds_data}
        :param audience: The audience to verify in the JWT received by the client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#audience AuthMethod#audience}
        :param gce: gce block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#gce AuthMethod#gce}
        :param iam: iam block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#iam AuthMethod#iam}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8079bed05e1c5aeab755ddaaf189ece7a449116b1b05d6c6af45075035ec5292)
            check_type(argname="argument service_account_creds_data", value=service_account_creds_data, expected_type=type_hints["service_account_creds_data"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument gce", value=gce, expected_type=type_hints["gce"])
            check_type(argname="argument iam", value=iam, expected_type=type_hints["iam"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "service_account_creds_data": service_account_creds_data,
        }
        if audience is not None:
            self._values["audience"] = audience
        if gce is not None:
            self._values["gce"] = gce
        if iam is not None:
            self._values["iam"] = iam

    @builtins.property
    def service_account_creds_data(self) -> builtins.str:
        '''Service Account creds data, base64 encoded.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#service_account_creds_data AuthMethod#service_account_creds_data}
        '''
        result = self._values.get("service_account_creds_data")
        assert result is not None, "Required property 'service_account_creds_data' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''The audience to verify in the JWT received by the client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#audience AuthMethod#audience}
        '''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gce(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcpGce"]]]:
        '''gce block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#gce AuthMethod#gce}
        '''
        result = self._values.get("gce")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcpGce"]]], result)

    @builtins.property
    def iam(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcpIam"]]]:
        '''iam block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#iam AuthMethod#iam}
        '''
        result = self._values.get("iam")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AuthMethodGcpIam"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodGcp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodGcpGce",
    jsii_struct_bases=[],
    name_mapping={
        "bound_labels": "boundLabels",
        "bound_regions": "boundRegions",
        "bound_zones": "boundZones",
    },
)
class AuthMethodGcpGce:
    def __init__(
        self,
        *,
        bound_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
        bound_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param bound_labels: GCE only. A list of GCP labels formatted as "key:value" pairs that must be set on instances in order to authenticate Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_labels AuthMethod#bound_labels}
        :param bound_regions: GCE only. A list of regions. GCE instances must belong to any of the provided regions in order to authenticate Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_regions AuthMethod#bound_regions}
        :param bound_zones: GCE only. A list of zones. GCE instances must belong to any of the provided zones in order to authenticate Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_zones AuthMethod#bound_zones}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0337a6d0f7b917a358b40af6adad1d433a12ae584f7559d9114c062d0601dbf1)
            check_type(argname="argument bound_labels", value=bound_labels, expected_type=type_hints["bound_labels"])
            check_type(argname="argument bound_regions", value=bound_regions, expected_type=type_hints["bound_regions"])
            check_type(argname="argument bound_zones", value=bound_zones, expected_type=type_hints["bound_zones"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bound_labels is not None:
            self._values["bound_labels"] = bound_labels
        if bound_regions is not None:
            self._values["bound_regions"] = bound_regions
        if bound_zones is not None:
            self._values["bound_zones"] = bound_zones

    @builtins.property
    def bound_labels(self) -> typing.Optional[typing.List[builtins.str]]:
        '''GCE only.

        A list of GCP labels formatted as "key:value" pairs that must be set on instances in order to authenticate

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_labels AuthMethod#bound_labels}
        '''
        result = self._values.get("bound_labels")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_regions(self) -> typing.Optional[typing.List[builtins.str]]:
        '''GCE only.

        A list of regions. GCE instances must belong to any of the provided regions in order to authenticate

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_regions AuthMethod#bound_regions}
        '''
        result = self._values.get("bound_regions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def bound_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        '''GCE only.

        A list of zones. GCE instances must belong to any of the provided zones in order to authenticate

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_zones AuthMethod#bound_zones}
        '''
        result = self._values.get("bound_zones")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodGcpGce(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthMethodGcpGceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodGcpGceList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a5153b3d07b7303ce881212a6da32fabf3052b528b6d0de617dd133e1c46e5c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AuthMethodGcpGceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1deeea4d302216ad244a4e59ceb2f43582e56ec6c0edc86089b7c95df4bb826a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthMethodGcpGceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5e7e0e543434df26fdee7fb8071d6eb7e9b0a71298969d94291381338922065)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02f20ce95cc64e5584cd8a6b8f1aea97f732d7eb5bf908e2c406ab463ec42bd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fdc32f57c333dff2a3a01952d4daabc503b231a4fa73ca86c3c161fc3674766)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpGce]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpGce]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpGce]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f3306a7ef059ae451b7437f3e686b116549ded7b13b442ca668d35976ca46e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodGcpGceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodGcpGceOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61252fec0dbe5517baa5de906346d8399b104ec8fdfa28b2e033d12467714536)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBoundLabels")
    def reset_bound_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundLabels", []))

    @jsii.member(jsii_name="resetBoundRegions")
    def reset_bound_regions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundRegions", []))

    @jsii.member(jsii_name="resetBoundZones")
    def reset_bound_zones(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundZones", []))

    @builtins.property
    @jsii.member(jsii_name="boundLabelsInput")
    def bound_labels_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundLabelsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundRegionsInput")
    def bound_regions_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundRegionsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundZonesInput")
    def bound_zones_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundZonesInput"))

    @builtins.property
    @jsii.member(jsii_name="boundLabels")
    def bound_labels(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundLabels"))

    @bound_labels.setter
    def bound_labels(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82be9a4ac7224b51f76fcae4c5047049980f5a9c56aace259ca5d79aa531f085)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundLabels", value)

    @builtins.property
    @jsii.member(jsii_name="boundRegions")
    def bound_regions(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundRegions"))

    @bound_regions.setter
    def bound_regions(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d77ca6811b2d1a3906b11bae4e4d4fe14c8438da5cf4b5d5f7b1266709685528)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundRegions", value)

    @builtins.property
    @jsii.member(jsii_name="boundZones")
    def bound_zones(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundZones"))

    @bound_zones.setter
    def bound_zones(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a8a691e7144881f3d3873148f5b738c7f5aba7cdd66c6851102ed4b40175ee1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundZones", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpGce]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpGce]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpGce]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a5e9c1f6e77c81e1821fe4dbf32ed2d4504ffd9d17ff58dbe53cdf294e1cec4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodGcpIam",
    jsii_struct_bases=[],
    name_mapping={"bound_service_accounts": "boundServiceAccounts"},
)
class AuthMethodGcpIam:
    def __init__(
        self,
        *,
        bound_service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param bound_service_accounts: IAM only. A list of Service Accounts. Clients must belong to any of the provided service accounts in order to authenticate Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_service_accounts AuthMethod#bound_service_accounts}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7eac982127d5b3fa4e05b8757bff53563c0de6fb651fb4cb238343623fab2db7)
            check_type(argname="argument bound_service_accounts", value=bound_service_accounts, expected_type=type_hints["bound_service_accounts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bound_service_accounts is not None:
            self._values["bound_service_accounts"] = bound_service_accounts

    @builtins.property
    def bound_service_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''IAM only.

        A list of Service Accounts. Clients must belong to any of the provided service accounts in order to authenticate

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#bound_service_accounts AuthMethod#bound_service_accounts}
        '''
        result = self._values.get("bound_service_accounts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodGcpIam(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthMethodGcpIamList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodGcpIamList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dfd540b7b1c729213903206a4e15fb067d56df4cc1571d01876f8750c702f25)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AuthMethodGcpIamOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a5f1a4a9f0561956550b7af6d744daa3257baa8a4de7ab131444251e00e663f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthMethodGcpIamOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5b7391a5c72bc537270430d1cbe905f1ae56e87db1094c951316af89287605a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ae874b5dbd8ba84dedd1cdd79ce956792a6c97b8b108eab1142766718e58247)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__780dc53cf108c8bda5f703b4117185b020c865bca4f755dce6179e8af358345c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpIam]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpIam]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpIam]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88d7d7b8ad74d21e17af0ceed827d0aabbf65d634b3ecc6fedacc1e00235c5c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodGcpIamOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodGcpIamOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b907702b7c1033f9fb12cc8b0d73dd3f51e78f8e56aa05b5ef5b0b1910a87ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBoundServiceAccounts")
    def reset_bound_service_accounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBoundServiceAccounts", []))

    @builtins.property
    @jsii.member(jsii_name="boundServiceAccountsInput")
    def bound_service_accounts_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "boundServiceAccountsInput"))

    @builtins.property
    @jsii.member(jsii_name="boundServiceAccounts")
    def bound_service_accounts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "boundServiceAccounts"))

    @bound_service_accounts.setter
    def bound_service_accounts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8051bec98ddfb5c30bd2bf9e56f9d3f03a640fbcd6399ee8f9c9e8e7a8687a21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "boundServiceAccounts", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpIam]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpIam]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpIam]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4a5256f09f0e822b0deb5991488bd57ae26a99dc82061439644d652de6c8cf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodGcpList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodGcpList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f21a14eadcd5e5d65639cb58d13b276d855260581e8765086002cdfc729e4fd9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AuthMethodGcpOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08d686883109728b0e4dafc06526f8b9155327350a2a9ee1cb7206c9c30b400d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthMethodGcpOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f368cd12d3f16b47e4a19e66a7c62de141b6e88103a25325b136fcee99a9558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc8b58ced899b4d8d47d6cd2cb071601cb98ce9975c1c556766075e46b6c39bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0542af417ad359a5b671c3a3bc5d377aedbbd82807ec3d8c5ed401eca2a68a7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcp]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcp]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcp]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60b5dd1b5d32f31fb7f9220313382bf186d4dd38af50623bd6def3a0e06a172c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodGcpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodGcpOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e40c17c3c1798f8eae204e52d8b6a9329e0bf1ced81df589aae461cdb666f9a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putGce")
    def put_gce(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcpGce, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__276e47e2f35693112c4c79a438dc2c056a20c98a9ab9849e2819888c58011007)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGce", [value]))

    @jsii.member(jsii_name="putIam")
    def put_iam(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcpIam, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df83f6f061bf5ce7725c70b576801215804857d669150c2b5cf02fe0f2dfcdd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putIam", [value]))

    @jsii.member(jsii_name="resetAudience")
    def reset_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudience", []))

    @jsii.member(jsii_name="resetGce")
    def reset_gce(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGce", []))

    @jsii.member(jsii_name="resetIam")
    def reset_iam(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIam", []))

    @builtins.property
    @jsii.member(jsii_name="gce")
    def gce(self) -> AuthMethodGcpGceList:
        return typing.cast(AuthMethodGcpGceList, jsii.get(self, "gce"))

    @builtins.property
    @jsii.member(jsii_name="iam")
    def iam(self) -> AuthMethodGcpIamList:
        return typing.cast(AuthMethodGcpIamList, jsii.get(self, "iam"))

    @builtins.property
    @jsii.member(jsii_name="audienceInput")
    def audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audienceInput"))

    @builtins.property
    @jsii.member(jsii_name="gceInput")
    def gce_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpGce]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpGce]]], jsii.get(self, "gceInput"))

    @builtins.property
    @jsii.member(jsii_name="iamInput")
    def iam_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpIam]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpIam]]], jsii.get(self, "iamInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountCredsDataInput")
    def service_account_creds_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountCredsDataInput"))

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__162e9d1d71c995c6d71c33346dbd04ecf860de51efecf3475f853604876a017e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value)

    @builtins.property
    @jsii.member(jsii_name="serviceAccountCredsData")
    def service_account_creds_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountCredsData"))

    @service_account_creds_data.setter
    def service_account_creds_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e880fdc62f933f6b8b22aab53cc7fe2741f934b9e4eaa70e63cef19da0157a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountCredsData", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcp]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcp]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcp]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ace3676be91e47ab30a60c1add3126ffdaf2c5dca54450a72b15e8431f1b1f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.authMethod.AuthMethodSaml",
    jsii_struct_bases=[],
    name_mapping={
        "unique_identifier": "uniqueIdentifier",
        "idp_metadata_url": "idpMetadataUrl",
        "idp_metadata_xml_data": "idpMetadataXmlData",
    },
)
class AuthMethodSaml:
    def __init__(
        self,
        *,
        unique_identifier: builtins.str,
        idp_metadata_url: typing.Optional[builtins.str] = None,
        idp_metadata_xml_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param unique_identifier: A unique identifier (ID) value should be configured for OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#unique_identifier AuthMethod#unique_identifier}
        :param idp_metadata_url: IDP metadata url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#idp_metadata_url AuthMethod#idp_metadata_url}
        :param idp_metadata_xml_data: IDP metadata xml data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#idp_metadata_xml_data AuthMethod#idp_metadata_xml_data}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__566cd0ef52010112e3a9f6c842afc3c2fc2ce4546205bdfe6dcbe495b8321eef)
            check_type(argname="argument unique_identifier", value=unique_identifier, expected_type=type_hints["unique_identifier"])
            check_type(argname="argument idp_metadata_url", value=idp_metadata_url, expected_type=type_hints["idp_metadata_url"])
            check_type(argname="argument idp_metadata_xml_data", value=idp_metadata_xml_data, expected_type=type_hints["idp_metadata_xml_data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "unique_identifier": unique_identifier,
        }
        if idp_metadata_url is not None:
            self._values["idp_metadata_url"] = idp_metadata_url
        if idp_metadata_xml_data is not None:
            self._values["idp_metadata_xml_data"] = idp_metadata_xml_data

    @builtins.property
    def unique_identifier(self) -> builtins.str:
        '''A unique identifier (ID) value should be configured for OAuth2, LDAP and SAML authentication method types and is usually a value such as the email, username, or upn for example.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#unique_identifier AuthMethod#unique_identifier}
        '''
        result = self._values.get("unique_identifier")
        assert result is not None, "Required property 'unique_identifier' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def idp_metadata_url(self) -> typing.Optional[builtins.str]:
        '''IDP metadata url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#idp_metadata_url AuthMethod#idp_metadata_url}
        '''
        result = self._values.get("idp_metadata_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_metadata_xml_data(self) -> typing.Optional[builtins.str]:
        '''IDP metadata xml data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/auth_method#idp_metadata_xml_data AuthMethod#idp_metadata_xml_data}
        '''
        result = self._values.get("idp_metadata_xml_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthMethodSaml(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuthMethodSamlList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodSamlList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__792fd9e752a4089a0b157e16edf5999ffd6e4fa2a5e00a39e8d18c202793ed27)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AuthMethodSamlOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98ec33fd0abbfe58c1a4eaf50319ee9a168c11717ce025e424ad82cc1e30d9f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AuthMethodSamlOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56f905d8f9c5cb3beafc85898e54903c9e82e57c1998fe786be8ead4091ed5c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6a62a024657dda095d041867d0460433c163dfeac2d8390e1119fc6d99c0e00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__442e0935d40e870ef7b5375f94ef266463132007be6804d75d500aac732ec7ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodSaml]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodSaml]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodSaml]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__536c8acd29cb5cd57bf4546f90b590b521685bba6f798256254c7d640b8b6cb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AuthMethodSamlOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.authMethod.AuthMethodSamlOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40039f2dbec8498219df97b4253b2fff88879657f0db932acf6768faca44acaf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetIdpMetadataUrl")
    def reset_idp_metadata_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpMetadataUrl", []))

    @jsii.member(jsii_name="resetIdpMetadataXmlData")
    def reset_idp_metadata_xml_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpMetadataXmlData", []))

    @builtins.property
    @jsii.member(jsii_name="idpMetadataUrlInput")
    def idp_metadata_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpMetadataUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="idpMetadataXmlDataInput")
    def idp_metadata_xml_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpMetadataXmlDataInput"))

    @builtins.property
    @jsii.member(jsii_name="uniqueIdentifierInput")
    def unique_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uniqueIdentifierInput"))

    @builtins.property
    @jsii.member(jsii_name="idpMetadataUrl")
    def idp_metadata_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpMetadataUrl"))

    @idp_metadata_url.setter
    def idp_metadata_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d89c42a439d8a8ec7018e9ed0ffb3f9b2035749c8f93bd25ac0f83fc41ea3a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpMetadataUrl", value)

    @builtins.property
    @jsii.member(jsii_name="idpMetadataXmlData")
    def idp_metadata_xml_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpMetadataXmlData"))

    @idp_metadata_xml_data.setter
    def idp_metadata_xml_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0dd319189b9e342499ef9ffd7923ff74ad735b9a51532a846b06da7114e4e59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpMetadataXmlData", value)

    @builtins.property
    @jsii.member(jsii_name="uniqueIdentifier")
    def unique_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uniqueIdentifier"))

    @unique_identifier.setter
    def unique_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b180f48d0d7c7c4bf5ca37c07182b9a3c701a21d44652f0ed57def2e1834f7f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uniqueIdentifier", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodSaml]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodSaml]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodSaml]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a68b89ace2ce52cb0b7074885950f479e6738ce667afe2bbbe8a71f278f87c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "AuthMethod",
    "AuthMethodApiKey",
    "AuthMethodApiKeyList",
    "AuthMethodApiKeyOutputReference",
    "AuthMethodAwsIam",
    "AuthMethodAwsIamList",
    "AuthMethodAwsIamOutputReference",
    "AuthMethodAzureAd",
    "AuthMethodAzureAdList",
    "AuthMethodAzureAdOutputReference",
    "AuthMethodConfig",
    "AuthMethodGcp",
    "AuthMethodGcpGce",
    "AuthMethodGcpGceList",
    "AuthMethodGcpGceOutputReference",
    "AuthMethodGcpIam",
    "AuthMethodGcpIamList",
    "AuthMethodGcpIamOutputReference",
    "AuthMethodGcpList",
    "AuthMethodGcpOutputReference",
    "AuthMethodSaml",
    "AuthMethodSamlList",
    "AuthMethodSamlOutputReference",
]

publication.publish()

def _typecheckingstub__7d1e97e9cc9decab009d97d74f1a8e1ef2a005005f3e6693d416908d64f60bd8(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    path: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_iam: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAwsIam, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_ad: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAzureAd, typing.Dict[builtins.str, typing.Any]]]]] = None,
    bound_ips: typing.Optional[builtins.str] = None,
    gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcp, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    saml: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodSaml, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__f0dbb0775477ff984b18a7ea1feff0a1508a99da8f3d36911b90e4b7ee63995f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2ece26020829f0c964d1da742edf6d9f7b39bc427a89a47396e9870f5d8b20e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodApiKey, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4be1997c14b598b9fb5664a335789fabc9766cf531429987c5b1b3a2530c5c3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAwsIam, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b80130d7419041e02a7d1cf7dcb07a07cf1a07a4e9bec5e470c2524d8333690(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAzureAd, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6607127be3d109d4b7a7965c0541e3c8c0bb5a3b92aa630af7535265ed649e7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcp, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15c7f85414a25a40a7919baf276dc324fe83966d3e7363ddd5efadf21da005a6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodSaml, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__432e4e495fc76a8b16c2b98a60ec0f91d5cf0caf18bb2a62f7eea3967a03aab4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__028f1c58aa86c2999103d1d0933b16d949e8d0429f8dfd74a0c0d4a7517d53b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfe2af6cd6aa1b4db4b76f4987ea363da41f4f0ee521a9e0607ab2005b66818d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab0ee09496e87161447b1c5d3d64257f8c45350fa7eee9dcb8b1da7d14eb0192(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fab80f5317e2563abef8e83f80c9f7a8af6ebe6d5aba99e03e8c6c4bdbe1578a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fcbc6ac897ad0e0597bff2ab7db290d30230d452ac7f09df0e43afcde930dc7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f2c0bab3d1bad583236723ddf05653a11deb4fe5d94ab20935a520bbb4e1515(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ca64cda6e295525754b07375194e7605fc40e6c18ef5b4b82d87c8d2d80209b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912c973247e6da2acd8989073bdebf235a31a922437ac2aa6a173baee389a3dd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16fbfe460dc76a74ddf4bb8a5e4242821fdb945b186b94e4337fcf6561ff972d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodApiKey]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21c20a10f8519728e9232a11c55207e7733bfdc4798fad77039a5409f727a001(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__617df0d4a1b9940dc8dc28f79a41cb0759877b7f4ddf411e7631369d2fb51303(
    value: typing.Optional[typing.Union[AuthMethodApiKey, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de6152d37409e8f6a71100fc9efe37940c4f828613ad0935f3773e0ff56b058c(
    *,
    bound_aws_account_id: typing.Sequence[builtins.str],
    bound_arn: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_role_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_role_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_user_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_user_name: typing.Optional[typing.Sequence[builtins.str]] = None,
    sts_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df6d29154280c28778b431fa4b238183a2d23e28e0691ed7163a61920c5153d0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7be0a2dfcbe8f5dfbff320a82984339c9328acba22cbbbe0566d54775555784(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd1fc76efe14eafdc34ad6714d8127f0489636fa4176ce97bfe261edaf599349(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c280d5addca4fba551748189744af24eb4e1a9e12954abf6e3ef57fa0309bc9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39f974e82641e5d53d99657fb8e81439385b65c86377f6be1e1daf7c5554d0cb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8822250633560b4e35f0eef9c9da56ac08c7cbd10a611f3b7ab0d232fb883b3c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAwsIam]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebe66538d198e9ab4dd8f0d6dd26b1923f007d9a3ba897d324a0b6c3c2d26ea4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__831756db896ce5bd9474aae18e8747dc0c0ef38826902fd895535ab4ce453330(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c95771696aaf2960637e19920812be301cad1eb288ca2c18352072b3f544c286(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1f2f1eae6102e97f4bb6b988f9bd67e0f6a74ae39c7aba52893c40836909ddb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469700b1194a5d669d85ceacf010a744b8b3cb93533d4f691cbd98c4b5b68f83(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74d397383d8c67e20dbfe0aa5892c1d34d1155831a6796cfde8a9503ed45d9ef(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__914f96af21c6ef77b057bc8d8309cc3719d34dd9dbba0468600407b00d15c82c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55bda56dac231dba92461bb7810366d1663c6e545859c7d5c8cb7675ca3de19b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c064d59dda42a7e995f5f9f4e989351edea1351bc331eee8859a1b1a51a908b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7080fba3b71ae7e04ae871c950812483d3bf75a1465d514cc74388c56a70fa16(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAwsIam]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c34d71caa10a23b05ad45d73a5372e6601d76c4b1a543a5453db225d6d8fc2d9(
    *,
    bound_tenant_id: builtins.str,
    bound_group_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_resource_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_rg_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_spid: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_sub_id: typing.Optional[typing.Sequence[builtins.str]] = None,
    custom_audience: typing.Optional[builtins.str] = None,
    custom_issuer: typing.Optional[builtins.str] = None,
    jwks_uri: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69c6d54c0bbd515d24d5995c26f53d2d9a5f1914b09bbf526989b0c352d11598(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__690593bb2496b5485e629256eb94a59ca6b7d369878b92db717cac17ce9837b5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64e3e8118260a9d94eae3a8817b66d44294e679d5c191a27d817db4aee2c600d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9e2ed3c302cd29d1a9173faa9feda059b31e55b96f3bb3b225de8297506c136(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b790ec5c09765b2659bea5f9f84933543bc9e7546fe17b88296604c6c60da334(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc8f3a013376f30b9151e61ae2e296370e1192ac03b4b15c3c081e6282332ab7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodAzureAd]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85cfe8fbcb025d806bd79b3d5dc5b62e36a11a82a193e2e2d61af2387abf849d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a241a5b650b2103def926755e841fb776cba74516060c0a795b1d56b5d5dc2b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e788752789dc3ee80364636f17b2c2a100f9a668f026dbdeb2520ece10c952(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ad3419b4d695b551919568bca4d70c71a88ae9099258e8c17e735e249fbedc8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44dc45b5d01128c4833305840915f2ef528790bb606d0f9e694e4a0a25fd138f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__707e9f3535c5c56bd12ca642082209cdc428085e896b7f5517b6df275796ad88(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28fd9308171736a97d238a391c8d70e9fb69421bacbfaad5bdc4a69621ac2f5d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0999ca36cc7378a5e8c30f0c29000e15b542136af18c735b403eb876f032a18d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0635aab420c793fe3543c7b34e4737d78c4cbc8898441a26f1445b53df70e5e2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dabd3458b606b78de7636e806d7c5ebd0802a0638071d01ee0f76aafe02009af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98f16ebdef1ea74ca028fc6156f8443711cd0cf4163556c7a93385da9ae9a1ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b6ba990e41220e3800d39bebd27bca68e33959700e96ae31772ae63e130f20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cd5da5b5cce2fc3a5add87619a5b471540dd01409cd337e3037e9d457166495(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9541747c3848edc4a4315256da656b1dae2a7d003a6f3b204e3698eabca57aa9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodAzureAd]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b180d7fe06451ef8d8caff42b4afea4cc77c5e3aaeee5b03ae7e19feb761a2a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    path: builtins.str,
    access_expires: typing.Optional[jsii.Number] = None,
    api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_iam: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAwsIam, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_ad: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodAzureAd, typing.Dict[builtins.str, typing.Any]]]]] = None,
    bound_ips: typing.Optional[builtins.str] = None,
    gcp: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcp, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    saml: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodSaml, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8079bed05e1c5aeab755ddaaf189ece7a449116b1b05d6c6af45075035ec5292(
    *,
    service_account_creds_data: builtins.str,
    audience: typing.Optional[builtins.str] = None,
    gce: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcpGce, typing.Dict[builtins.str, typing.Any]]]]] = None,
    iam: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcpIam, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0337a6d0f7b917a358b40af6adad1d433a12ae584f7559d9114c062d0601dbf1(
    *,
    bound_labels: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_regions: typing.Optional[typing.Sequence[builtins.str]] = None,
    bound_zones: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a5153b3d07b7303ce881212a6da32fabf3052b528b6d0de617dd133e1c46e5c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1deeea4d302216ad244a4e59ceb2f43582e56ec6c0edc86089b7c95df4bb826a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5e7e0e543434df26fdee7fb8071d6eb7e9b0a71298969d94291381338922065(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02f20ce95cc64e5584cd8a6b8f1aea97f732d7eb5bf908e2c406ab463ec42bd9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fdc32f57c333dff2a3a01952d4daabc503b231a4fa73ca86c3c161fc3674766(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f3306a7ef059ae451b7437f3e686b116549ded7b13b442ca668d35976ca46e0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpGce]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61252fec0dbe5517baa5de906346d8399b104ec8fdfa28b2e033d12467714536(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82be9a4ac7224b51f76fcae4c5047049980f5a9c56aace259ca5d79aa531f085(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d77ca6811b2d1a3906b11bae4e4d4fe14c8438da5cf4b5d5f7b1266709685528(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a8a691e7144881f3d3873148f5b738c7f5aba7cdd66c6851102ed4b40175ee1(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a5e9c1f6e77c81e1821fe4dbf32ed2d4504ffd9d17ff58dbe53cdf294e1cec4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpGce]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7eac982127d5b3fa4e05b8757bff53563c0de6fb651fb4cb238343623fab2db7(
    *,
    bound_service_accounts: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dfd540b7b1c729213903206a4e15fb067d56df4cc1571d01876f8750c702f25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a5f1a4a9f0561956550b7af6d744daa3257baa8a4de7ab131444251e00e663f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5b7391a5c72bc537270430d1cbe905f1ae56e87db1094c951316af89287605a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ae874b5dbd8ba84dedd1cdd79ce956792a6c97b8b108eab1142766718e58247(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__780dc53cf108c8bda5f703b4117185b020c865bca4f755dce6179e8af358345c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88d7d7b8ad74d21e17af0ceed827d0aabbf65d634b3ecc6fedacc1e00235c5c7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcpIam]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b907702b7c1033f9fb12cc8b0d73dd3f51e78f8e56aa05b5ef5b0b1910a87ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8051bec98ddfb5c30bd2bf9e56f9d3f03a640fbcd6399ee8f9c9e8e7a8687a21(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4a5256f09f0e822b0deb5991488bd57ae26a99dc82061439644d652de6c8cf7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcpIam]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f21a14eadcd5e5d65639cb58d13b276d855260581e8765086002cdfc729e4fd9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08d686883109728b0e4dafc06526f8b9155327350a2a9ee1cb7206c9c30b400d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f368cd12d3f16b47e4a19e66a7c62de141b6e88103a25325b136fcee99a9558(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc8b58ced899b4d8d47d6cd2cb071601cb98ce9975c1c556766075e46b6c39bb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0542af417ad359a5b671c3a3bc5d377aedbbd82807ec3d8c5ed401eca2a68a7e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60b5dd1b5d32f31fb7f9220313382bf186d4dd38af50623bd6def3a0e06a172c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodGcp]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e40c17c3c1798f8eae204e52d8b6a9329e0bf1ced81df589aae461cdb666f9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__276e47e2f35693112c4c79a438dc2c056a20c98a9ab9849e2819888c58011007(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcpGce, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df83f6f061bf5ce7725c70b576801215804857d669150c2b5cf02fe0f2dfcdd8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AuthMethodGcpIam, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__162e9d1d71c995c6d71c33346dbd04ecf860de51efecf3475f853604876a017e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e880fdc62f933f6b8b22aab53cc7fe2741f934b9e4eaa70e63cef19da0157a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ace3676be91e47ab30a60c1add3126ffdaf2c5dca54450a72b15e8431f1b1f5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodGcp]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__566cd0ef52010112e3a9f6c842afc3c2fc2ce4546205bdfe6dcbe495b8321eef(
    *,
    unique_identifier: builtins.str,
    idp_metadata_url: typing.Optional[builtins.str] = None,
    idp_metadata_xml_data: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__792fd9e752a4089a0b157e16edf5999ffd6e4fa2a5e00a39e8d18c202793ed27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98ec33fd0abbfe58c1a4eaf50319ee9a168c11717ce025e424ad82cc1e30d9f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56f905d8f9c5cb3beafc85898e54903c9e82e57c1998fe786be8ead4091ed5c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6a62a024657dda095d041867d0460433c163dfeac2d8390e1119fc6d99c0e00(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__442e0935d40e870ef7b5375f94ef266463132007be6804d75d500aac732ec7ae(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__536c8acd29cb5cd57bf4546f90b590b521685bba6f798256254c7d640b8b6cb3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AuthMethodSaml]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40039f2dbec8498219df97b4253b2fff88879657f0db932acf6768faca44acaf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d89c42a439d8a8ec7018e9ed0ffb3f9b2035749c8f93bd25ac0f83fc41ea3a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0dd319189b9e342499ef9ffd7923ff74ad735b9a51532a846b06da7114e4e59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b180f48d0d7c7c4bf5ca37c07182b9a3c701a21d44652f0ed57def2e1834f7f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a68b89ace2ce52cb0b7074885950f479e6738ce667afe2bbbe8a71f278f87c5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AuthMethodSaml]],
) -> None:
    """Type checking stubs"""
    pass
