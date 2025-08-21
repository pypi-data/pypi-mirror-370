'''
# `data_akeyless_auth`

Refer to the Terraform Registry for docs: [`data_akeyless_auth`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth).
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


class DataAkeylessAuth(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuth",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth akeyless_auth}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthApiKeyLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthAwsIamLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthAzureAdLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthCertLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthEmailLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthGcpLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthJwtLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthUidLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth akeyless_auth} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param api_key_login: api_key_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#api_key_login DataAkeylessAuth#api_key_login}
        :param aws_iam_login: aws_iam_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#aws_iam_login DataAkeylessAuth#aws_iam_login}
        :param azure_ad_login: azure_ad_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#azure_ad_login DataAkeylessAuth#azure_ad_login}
        :param cert_login: cert_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#cert_login DataAkeylessAuth#cert_login}
        :param email_login: email_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#email_login DataAkeylessAuth#email_login}
        :param gcp_login: gcp_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#gcp_login DataAkeylessAuth#gcp_login}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#id DataAkeylessAuth#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_login: jwt_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#jwt_login DataAkeylessAuth#jwt_login}
        :param uid_login: uid_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#uid_login DataAkeylessAuth#uid_login}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7298ab4ef3e9bb1a091ca027f1512e301f846a47813dd1aa67c06c9b7203f033)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataAkeylessAuthConfig(
            api_key_login=api_key_login,
            aws_iam_login=aws_iam_login,
            azure_ad_login=azure_ad_login,
            cert_login=cert_login,
            email_login=email_login,
            gcp_login=gcp_login,
            id=id,
            jwt_login=jwt_login,
            uid_login=uid_login,
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
        '''Generates CDKTF code for importing a DataAkeylessAuth resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataAkeylessAuth to import.
        :param import_from_id: The id of the existing DataAkeylessAuth that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataAkeylessAuth to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f21f1b2664af080a7bfc29ec1400924b2ff40aba166fcc5a2510ca755809758)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putApiKeyLogin")
    def put_api_key_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthApiKeyLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a484d072358ecd400e2bebe77906dec109e85168983ee81dc9c329a8e0b1d2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeyLogin", [value]))

    @jsii.member(jsii_name="putAwsIamLogin")
    def put_aws_iam_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthAwsIamLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4bbf6b692abce839070db4d89f87f0bff3eb8646344ba492fd8c6d32eac51b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAwsIamLogin", [value]))

    @jsii.member(jsii_name="putAzureAdLogin")
    def put_azure_ad_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthAzureAdLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9f3adff41d9658bed8f1b5d9d0b3314939bb7bec0eb17bbd9df6c54a84c635)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAzureAdLogin", [value]))

    @jsii.member(jsii_name="putCertLogin")
    def put_cert_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthCertLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea674be7961be5f446e5c10b32657dd19cb851bafc67c73c0bbf3c8e046730ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCertLogin", [value]))

    @jsii.member(jsii_name="putEmailLogin")
    def put_email_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthEmailLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0efed4e53c1ea04ca2e2b68a4bc7be1b8d98cdaaab49d31b9adcf8728a1fa547)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEmailLogin", [value]))

    @jsii.member(jsii_name="putGcpLogin")
    def put_gcp_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthGcpLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bf49ca1003318f0bc67785e5ddf40fd660f6ea2aa90954c9e56371e85ae72b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGcpLogin", [value]))

    @jsii.member(jsii_name="putJwtLogin")
    def put_jwt_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthJwtLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb38c709e3aaeeab7f88026504e9b6d92b89f548549ea92309aa59d67e1253bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putJwtLogin", [value]))

    @jsii.member(jsii_name="putUidLogin")
    def put_uid_login(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthUidLogin", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48921f2a567a2203c40dc1de40d5d8a547d86714bae9e5bebc00394a461b65cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUidLogin", [value]))

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

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetJwtLogin")
    def reset_jwt_login(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJwtLogin", []))

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
    @jsii.member(jsii_name="apiKeyLogin")
    def api_key_login(self) -> "DataAkeylessAuthApiKeyLoginList":
        return typing.cast("DataAkeylessAuthApiKeyLoginList", jsii.get(self, "apiKeyLogin"))

    @builtins.property
    @jsii.member(jsii_name="awsIamLogin")
    def aws_iam_login(self) -> "DataAkeylessAuthAwsIamLoginList":
        return typing.cast("DataAkeylessAuthAwsIamLoginList", jsii.get(self, "awsIamLogin"))

    @builtins.property
    @jsii.member(jsii_name="azureAdLogin")
    def azure_ad_login(self) -> "DataAkeylessAuthAzureAdLoginList":
        return typing.cast("DataAkeylessAuthAzureAdLoginList", jsii.get(self, "azureAdLogin"))

    @builtins.property
    @jsii.member(jsii_name="certLogin")
    def cert_login(self) -> "DataAkeylessAuthCertLoginList":
        return typing.cast("DataAkeylessAuthCertLoginList", jsii.get(self, "certLogin"))

    @builtins.property
    @jsii.member(jsii_name="emailLogin")
    def email_login(self) -> "DataAkeylessAuthEmailLoginList":
        return typing.cast("DataAkeylessAuthEmailLoginList", jsii.get(self, "emailLogin"))

    @builtins.property
    @jsii.member(jsii_name="gcpLogin")
    def gcp_login(self) -> "DataAkeylessAuthGcpLoginList":
        return typing.cast("DataAkeylessAuthGcpLoginList", jsii.get(self, "gcpLogin"))

    @builtins.property
    @jsii.member(jsii_name="jwtLogin")
    def jwt_login(self) -> "DataAkeylessAuthJwtLoginList":
        return typing.cast("DataAkeylessAuthJwtLoginList", jsii.get(self, "jwtLogin"))

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "token"))

    @builtins.property
    @jsii.member(jsii_name="uidLogin")
    def uid_login(self) -> "DataAkeylessAuthUidLoginList":
        return typing.cast("DataAkeylessAuthUidLoginList", jsii.get(self, "uidLogin"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyLoginInput")
    def api_key_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthApiKeyLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthApiKeyLogin"]]], jsii.get(self, "apiKeyLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="awsIamLoginInput")
    def aws_iam_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthAwsIamLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthAwsIamLogin"]]], jsii.get(self, "awsIamLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="azureAdLoginInput")
    def azure_ad_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthAzureAdLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthAzureAdLogin"]]], jsii.get(self, "azureAdLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="certLoginInput")
    def cert_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthCertLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthCertLogin"]]], jsii.get(self, "certLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="emailLoginInput")
    def email_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthEmailLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthEmailLogin"]]], jsii.get(self, "emailLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpLoginInput")
    def gcp_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthGcpLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthGcpLogin"]]], jsii.get(self, "gcpLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtLoginInput")
    def jwt_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthJwtLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthJwtLogin"]]], jsii.get(self, "jwtLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="uidLoginInput")
    def uid_login_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthUidLogin"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthUidLogin"]]], jsii.get(self, "uidLoginInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f3699903aba51a787ec909aae11b8a630aff5c8aa336c30a7bfc29bf992e68d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthApiKeyLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId", "access_key": "accessKey"},
)
class DataAkeylessAuthApiKeyLogin:
    def __init__(self, *, access_id: builtins.str, access_key: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.
        :param access_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_key DataAkeylessAuth#access_key}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3354f26069c1bff5d65f08c2ba881c08400eb9b86e7fb39ee374c65a252de26a)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument access_key", value=access_key, expected_type=type_hints["access_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
            "access_key": access_key,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_key DataAkeylessAuth#access_key}.'''
        result = self._values.get("access_key")
        assert result is not None, "Required property 'access_key' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthApiKeyLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthApiKeyLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthApiKeyLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70b67173a65e4a410909f102a72a013ce2e6eaebe26a5e5539cfa067a9a1ca92)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthApiKeyLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b783b35b6ee3d262422d943bc4bada512e8711905ec0f66ef0487a73c70a9dc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthApiKeyLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d0bd6f070ab40f696b7a22a0c3c9206a2e473168cf4d34835e46d8b412be734)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cfe163cbacb41ebd0960be510e54cf1ca746184471f6f8735e223c6475969e01)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb316e45628e361214db6b96961635b90a8e2a8ff8a2c67fa195f9b5118df878)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthApiKeyLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthApiKeyLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthApiKeyLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b67eb4e3d1f034ef84c6c2a47edea923edfae51353d8d8235449b3488b776f27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthApiKeyLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthApiKeyLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0dfb9296459c80ec64b7f74ff283e0ed049ee431e37f9540669c523724a264ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accessKeyInput")
    def access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8155265e1c25351cb8ab6849c9c6405b80bcb4d7514b17095e38a628136d801c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="accessKey")
    def access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKey"))

    @access_key.setter
    def access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f52603dbfb2df56fc0b4ef66531c3af4c484d66ae4c92811804be426ec290a44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessKey", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthApiKeyLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthApiKeyLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthApiKeyLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b951b2f2dfbe401c04108cb4d2a76815f0884c220cead0efececc6e8546ad4ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthAwsIamLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId"},
)
class DataAkeylessAuthAwsIamLogin:
    def __init__(self, *, access_id: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12f11e15b3d4e1f268260721e0bb8c2558947fb576fcdabdf1f84b13e2dec07f)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthAwsIamLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthAwsIamLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthAwsIamLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__95384a78d733cef114cc50ed9cf13c0d839ea8a60ded43c4a3841cd20d1023b8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthAwsIamLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43e95f072588e8da00e19479c72c4d7382cdf15d1401699ea221b48a5a1c83be)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthAwsIamLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4afb1b3855ea47589a54fd6ca2e2c533172a69f5c97d1a6032d76931ab4140b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28d1b10087b89f1e556f3d77e60c2658ae8af65d896f35206337faf6a690dee2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__57cc1e218dd753411921e2606a02aa9f01c838e2c35d2e6bd7391aed66f70fa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAwsIamLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAwsIamLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAwsIamLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5797ebfa1baebb1f06199cbbc49a6ae73d25aaad3a32503fb332f94b9f011c60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthAwsIamLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthAwsIamLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__36bfd631a70687f36cf3ac022b086e74bba12423b236ebf51bd961dccf5c3175)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38977924b9b84495abee8563b8cb0c80a0bfea5e1de043e1665898c70fd3a224)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAwsIamLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAwsIamLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAwsIamLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b104859e997986e7802f1fdf602d4c2f44d47fc5b3e25afb343cf9d51a8c975e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthAzureAdLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId"},
)
class DataAkeylessAuthAzureAdLogin:
    def __init__(self, *, access_id: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dfc161b0dedf328ffbc5cf678f37929d3b48bca2901b33a01b2206cfc72d562)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthAzureAdLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthAzureAdLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthAzureAdLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2e094b8c098ac2831718e5b400e5cea95038c61627ba68156ce9f46af9c9442)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthAzureAdLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91b7ba43d87eefd3d612e555a56d274d0152210c98d1efe8e9b64fb7128a68d1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthAzureAdLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be92dc2913d21cb68d4bec4ff8e149f8997396e1daf6064cac23061a2a301a0c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a25d0b5ec74f012e27446eda3dd528e56a4f428ec165e315ffa3f201f70f7ed7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__246533fb8b32fb64fb70248bfe64fe50319318b02f83d6ee0f997f75aa3808d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAzureAdLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAzureAdLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAzureAdLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__491436b5c8ddc9735a2e34eb54cbe1f0b7a424f4aa0b67adb01ec6fa6758d27f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthAzureAdLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthAzureAdLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf9607a7a9c4ab0e2df8c675c4a4e717eb1b2497b66e2d7621bcb2c8d6448a86)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__852dca0229f42226a8832af346f103f468a831f58f225163cce57cea094f5455)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAzureAdLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAzureAdLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAzureAdLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6aaba41db53741bce08f01fbab47dd52fc8755661be67c6a97ee26bc1432c89e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthCertLogin",
    jsii_struct_bases=[],
    name_mapping={
        "access_id": "accessId",
        "cert_data": "certData",
        "cert_file_name": "certFileName",
        "key_data": "keyData",
        "key_file_name": "keyFileName",
    },
)
class DataAkeylessAuthCertLogin:
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
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.
        :param cert_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#cert_data DataAkeylessAuth#cert_data}.
        :param cert_file_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#cert_file_name DataAkeylessAuth#cert_file_name}.
        :param key_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#key_data DataAkeylessAuth#key_data}.
        :param key_file_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#key_file_name DataAkeylessAuth#key_file_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80a72db72549b7685d437cff57d63831e3678282d91d30eabf8b6de386521113)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cert_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#cert_data DataAkeylessAuth#cert_data}.'''
        result = self._values.get("cert_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_file_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#cert_file_name DataAkeylessAuth#cert_file_name}.'''
        result = self._values.get("cert_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#key_data DataAkeylessAuth#key_data}.'''
        result = self._values.get("key_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_file_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#key_file_name DataAkeylessAuth#key_file_name}.'''
        result = self._values.get("key_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthCertLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthCertLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthCertLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__14f683772cf616599f258e20105c0a6b13dc1fd33799e60e17e34fbb41636470)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthCertLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f917be5fe48cda885bf9c406a2192c39515f995aa64c8b53676f4115840cdacb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthCertLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34aaa76ffca92c0839de513527fb30610b4deff9f0632b5bcf0cea2cc8149b79)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6626aaf8fc354617de952f9de8ecafbaf52fa575e4374bd62b41efa8b53bb9e7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa8aaceda54ee395af5c724a5b11345500664f384618658509c303cb2636f54e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthCertLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthCertLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthCertLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__792bf688675ccc055b75c3c62f063ce929375b3005b7683d6ab74d4a46d100f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthCertLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthCertLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__07312dbf71c7ccda634d5c42bca4985b616f10778566812e330d2bbdbb01a542)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCertData")
    def reset_cert_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertData", []))

    @jsii.member(jsii_name="resetCertFileName")
    def reset_cert_file_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertFileName", []))

    @jsii.member(jsii_name="resetKeyData")
    def reset_key_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyData", []))

    @jsii.member(jsii_name="resetKeyFileName")
    def reset_key_file_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyFileName", []))

    @builtins.property
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="certDataInput")
    def cert_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certDataInput"))

    @builtins.property
    @jsii.member(jsii_name="certFileNameInput")
    def cert_file_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certFileNameInput"))

    @builtins.property
    @jsii.member(jsii_name="keyDataInput")
    def key_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyDataInput"))

    @builtins.property
    @jsii.member(jsii_name="keyFileNameInput")
    def key_file_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyFileNameInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__958e7559636db0e1f1039a614ee4f72f2d53e4eb264104c04871962b7145ca7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="certData")
    def cert_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certData"))

    @cert_data.setter
    def cert_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b35f1b0d4636f3cddb27227f60fa2a0a844fb827b62d938a08399dc7ca139efa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certData", value)

    @builtins.property
    @jsii.member(jsii_name="certFileName")
    def cert_file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certFileName"))

    @cert_file_name.setter
    def cert_file_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2236af54ba5368214f797a553e84735d7f2546b7726b04b1125815d876b74974)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certFileName", value)

    @builtins.property
    @jsii.member(jsii_name="keyData")
    def key_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyData"))

    @key_data.setter
    def key_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e98261161216c2c5e8e87ef7ff28f1f2af908705c209986032e8731c3605c166)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyData", value)

    @builtins.property
    @jsii.member(jsii_name="keyFileName")
    def key_file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyFileName"))

    @key_file_name.setter
    def key_file_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cf1812ef747318863f649e8f7c0df99828ffd42ce80fe59e5029115fc662c72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyFileName", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthCertLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthCertLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthCertLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4f312c1ef002e520b15add3bd364d37925c079c8aa6a9035a0bcbafb7a5df97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "api_key_login": "apiKeyLogin",
        "aws_iam_login": "awsIamLogin",
        "azure_ad_login": "azureAdLogin",
        "cert_login": "certLogin",
        "email_login": "emailLogin",
        "gcp_login": "gcpLogin",
        "id": "id",
        "jwt_login": "jwtLogin",
        "uid_login": "uidLogin",
    },
)
class DataAkeylessAuthConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthApiKeyLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAwsIamLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAzureAdLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthCertLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
        email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthEmailLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthGcpLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthJwtLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
        uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAkeylessAuthUidLogin", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param api_key_login: api_key_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#api_key_login DataAkeylessAuth#api_key_login}
        :param aws_iam_login: aws_iam_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#aws_iam_login DataAkeylessAuth#aws_iam_login}
        :param azure_ad_login: azure_ad_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#azure_ad_login DataAkeylessAuth#azure_ad_login}
        :param cert_login: cert_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#cert_login DataAkeylessAuth#cert_login}
        :param email_login: email_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#email_login DataAkeylessAuth#email_login}
        :param gcp_login: gcp_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#gcp_login DataAkeylessAuth#gcp_login}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#id DataAkeylessAuth#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param jwt_login: jwt_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#jwt_login DataAkeylessAuth#jwt_login}
        :param uid_login: uid_login block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#uid_login DataAkeylessAuth#uid_login}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eb0e7588d9fa550f79cfb161fe36b7ca67dc3acebba6838ba26256c2aedb091)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument api_key_login", value=api_key_login, expected_type=type_hints["api_key_login"])
            check_type(argname="argument aws_iam_login", value=aws_iam_login, expected_type=type_hints["aws_iam_login"])
            check_type(argname="argument azure_ad_login", value=azure_ad_login, expected_type=type_hints["azure_ad_login"])
            check_type(argname="argument cert_login", value=cert_login, expected_type=type_hints["cert_login"])
            check_type(argname="argument email_login", value=email_login, expected_type=type_hints["email_login"])
            check_type(argname="argument gcp_login", value=gcp_login, expected_type=type_hints["gcp_login"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument jwt_login", value=jwt_login, expected_type=type_hints["jwt_login"])
            check_type(argname="argument uid_login", value=uid_login, expected_type=type_hints["uid_login"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if id is not None:
            self._values["id"] = id
        if jwt_login is not None:
            self._values["jwt_login"] = jwt_login
        if uid_login is not None:
            self._values["uid_login"] = uid_login

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
    def api_key_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthApiKeyLogin]]]:
        '''api_key_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#api_key_login DataAkeylessAuth#api_key_login}
        '''
        result = self._values.get("api_key_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthApiKeyLogin]]], result)

    @builtins.property
    def aws_iam_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAwsIamLogin]]]:
        '''aws_iam_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#aws_iam_login DataAkeylessAuth#aws_iam_login}
        '''
        result = self._values.get("aws_iam_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAwsIamLogin]]], result)

    @builtins.property
    def azure_ad_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAzureAdLogin]]]:
        '''azure_ad_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#azure_ad_login DataAkeylessAuth#azure_ad_login}
        '''
        result = self._values.get("azure_ad_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAzureAdLogin]]], result)

    @builtins.property
    def cert_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthCertLogin]]]:
        '''cert_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#cert_login DataAkeylessAuth#cert_login}
        '''
        result = self._values.get("cert_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthCertLogin]]], result)

    @builtins.property
    def email_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthEmailLogin"]]]:
        '''email_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#email_login DataAkeylessAuth#email_login}
        '''
        result = self._values.get("email_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthEmailLogin"]]], result)

    @builtins.property
    def gcp_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthGcpLogin"]]]:
        '''gcp_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#gcp_login DataAkeylessAuth#gcp_login}
        '''
        result = self._values.get("gcp_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthGcpLogin"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#id DataAkeylessAuth#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def jwt_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthJwtLogin"]]]:
        '''jwt_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#jwt_login DataAkeylessAuth#jwt_login}
        '''
        result = self._values.get("jwt_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthJwtLogin"]]], result)

    @builtins.property
    def uid_login(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthUidLogin"]]]:
        '''uid_login block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#uid_login DataAkeylessAuth#uid_login}
        '''
        result = self._values.get("uid_login")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAkeylessAuthUidLogin"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthEmailLogin",
    jsii_struct_bases=[],
    name_mapping={"admin_email": "adminEmail", "admin_password": "adminPassword"},
)
class DataAkeylessAuthEmailLogin:
    def __init__(
        self,
        *,
        admin_email: builtins.str,
        admin_password: builtins.str,
    ) -> None:
        '''
        :param admin_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#admin_email DataAkeylessAuth#admin_email}.
        :param admin_password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#admin_password DataAkeylessAuth#admin_password}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64efbf48d114457193ebb98dc9cbd7f91d3ffce3731abcb5f7ae1622d887051c)
            check_type(argname="argument admin_email", value=admin_email, expected_type=type_hints["admin_email"])
            check_type(argname="argument admin_password", value=admin_password, expected_type=type_hints["admin_password"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "admin_email": admin_email,
            "admin_password": admin_password,
        }

    @builtins.property
    def admin_email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#admin_email DataAkeylessAuth#admin_email}.'''
        result = self._values.get("admin_email")
        assert result is not None, "Required property 'admin_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def admin_password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#admin_password DataAkeylessAuth#admin_password}.'''
        result = self._values.get("admin_password")
        assert result is not None, "Required property 'admin_password' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthEmailLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthEmailLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthEmailLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3870b5fd60723498e64b3495e92b68be6dd01c48682256c8b42e4e8b3e28909b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthEmailLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fb3015857020dac89c7c1be7a83abf2e509954d1d06304e2a8381591fba219b)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthEmailLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61d4bd83bdf9ad8feef77105227e8a8fd3272416f7c1988bf80977ba7daacd0c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2d6a3ab9de4291c0b1882751083104b30a400901820a19c635c4d64810e5bcf0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__48ec0020fdc0b87f0f4d58613cf2d41b8120d71dff70a3b1f7d54438dd3533f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthEmailLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthEmailLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthEmailLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30027d9bce148ba2b34c16fa88944fa45aa0fd4ee43cb62eabb24af3f1dc09ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthEmailLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthEmailLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__57951e0ed64ca1b09ce939ea7a85ba94ecbdcb60ce8b8d2b89ccc3a37aacc12e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="adminEmailInput")
    def admin_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="adminPasswordInput")
    def admin_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "adminPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="adminEmail")
    def admin_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminEmail"))

    @admin_email.setter
    def admin_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98c52ca9eab9c8f0fd6ac3b09f6a20f082364dc7285a96af5b8c2ddef6388b28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminEmail", value)

    @builtins.property
    @jsii.member(jsii_name="adminPassword")
    def admin_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "adminPassword"))

    @admin_password.setter
    def admin_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab0b3e1ed68adc2420ecc29a54c463c3df181230a0e2cc80bca6425f12f4cd96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "adminPassword", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthEmailLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthEmailLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthEmailLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e45aee314ba3d11631f02050a0bc4ebe80f7f22dbd2fb78ea0544fee80d3737)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthGcpLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId", "audience": "audience"},
)
class DataAkeylessAuthGcpLogin:
    def __init__(
        self,
        *,
        access_id: builtins.str,
        audience: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.
        :param audience: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#audience DataAkeylessAuth#audience}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a47d7bab5420732084146c3e3a7f282fcc84adc410506d7667f50558501a7f68)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
        }
        if audience is not None:
            self._values["audience"] = audience

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#audience DataAkeylessAuth#audience}.'''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthGcpLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthGcpLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthGcpLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__47733dbca838ba5b0103c435c5c0e3a4d278aaa28e38e611d66f4478b30fe17e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthGcpLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9a96925870df5a42f526312a9235b387b7289a45d07655e81f979109ad52f53)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthGcpLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba9e3520b3e09cf33be8dc193336410d532dce01121da59dccf69844871f4a31)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d428cb149cefe17b69627301e2ad268fe2550a7946d158af8330930a5743a01c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fadd776dc7337deeae13fbdfd16fe20ffa36dff7d1f0f60d345e60804dff6822)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthGcpLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthGcpLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthGcpLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f49b708b750a079eb5504777d3804b47bc764672bce0e6d673cdc4c8b1dbc42d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthGcpLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthGcpLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__47f366a60289d5ed47ab9d4ec5fdc81f59038843b4077a53c86b8500da4a6eb8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAudience")
    def reset_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudience", []))

    @builtins.property
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="audienceInput")
    def audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audienceInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abdf7181db64cd7cc4ec13e9a8cffd33462326b69c162fe628a1ce729eccbb3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bcef6bf8693856aac4c215f772f48b0f2304aea6930cc15ce4f806171be3eac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthGcpLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthGcpLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthGcpLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f743bb01d913f633cba6d3b6b42a8d3473397f1a239b42b7b4ea3b0d19b557a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthJwtLogin",
    jsii_struct_bases=[],
    name_mapping={"access_id": "accessId", "jwt": "jwt"},
)
class DataAkeylessAuthJwtLogin:
    def __init__(self, *, access_id: builtins.str, jwt: builtins.str) -> None:
        '''
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.
        :param jwt: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#jwt DataAkeylessAuth#jwt}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d91ff787ec556ff7136f5a74510c4e2b7dd13a07d88a228d92c070af72caf78)
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument jwt", value=jwt, expected_type=type_hints["jwt"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
            "jwt": jwt,
        }

    @builtins.property
    def access_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.'''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def jwt(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#jwt DataAkeylessAuth#jwt}.'''
        result = self._values.get("jwt")
        assert result is not None, "Required property 'jwt' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthJwtLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthJwtLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthJwtLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__19deb411573b9c6b7bd91047160b58ec8f0f137aa8817692ab637b3a2d74e935)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthJwtLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99b8cbbf9035d9af589684843a13ffc8e724f55c84f145bef184c41a92f06164)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthJwtLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77c39d4e0ab799d4eb214b743eeb2c2c102059017b65f501a29a54511e2124f9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9843edbb1c50e85e9cfd823407f68d9ba3af014b85889dea3fc8c4fac335dc42)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e094a8eb7394dc849416fc9993c69c0722e7f130ccbbaf5c335753d6bb968782)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthJwtLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthJwtLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthJwtLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dd3aebda9396182107a90508a7172c81619f363864fd94c4871da870da648ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthJwtLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthJwtLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__852a30b97c346bc07bdc0e4abe073950ecce59251fe98603dedbcd0c580946ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="jwtInput")
    def jwt_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "jwtInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__007bc14a8b2b2b1503597fe9f9f3ffbc65d8322b4af1ee249ef218baa8ba5c63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="jwt")
    def jwt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "jwt"))

    @jwt.setter
    def jwt(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bccbdbfe5b9c400f3ba4dab9c49c43ceaeb50649b1aa654a7eb0199de86c423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jwt", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthJwtLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthJwtLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthJwtLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ca952d5e29f84c79365d041a0597e562f003a4ac3aa6979a4257e6f9b845e26)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthUidLogin",
    jsii_struct_bases=[],
    name_mapping={"uid_token": "uidToken", "access_id": "accessId"},
)
class DataAkeylessAuthUidLogin:
    def __init__(
        self,
        *,
        uid_token: builtins.str,
        access_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param uid_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#uid_token DataAkeylessAuth#uid_token}.
        :param access_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05b42ce646de641f35ca8ec9c3059fc862b586388255f32ff28bb225853ebeb7)
            check_type(argname="argument uid_token", value=uid_token, expected_type=type_hints["uid_token"])
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "uid_token": uid_token,
        }
        if access_id is not None:
            self._values["access_id"] = access_id

    @builtins.property
    def uid_token(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#uid_token DataAkeylessAuth#uid_token}.'''
        result = self._values.get("uid_token")
        assert result is not None, "Required property 'uid_token' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def access_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/data-sources/auth#access_id DataAkeylessAuth#access_id}.'''
        result = self._values.get("access_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAkeylessAuthUidLogin(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAkeylessAuthUidLoginList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthUidLoginList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8843ad2377a20272a90392ff5cea1d1cbb8d2da1000fb75aa8142c663be55ef7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataAkeylessAuthUidLoginOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de0a71d8ae4cf388a73dd091ba695ac870354e2c733373a1f33a594e7621916e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAkeylessAuthUidLoginOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b9ca762811fa92485ed1179ce24573112eae93d5a6255a6f88189601ca1b8f9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f604ce996d99aa1a2256757d4dee42f7dfc4d30d65c41ca563c5cc672dcff77c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dce18985e2fe2a637622ee080dabc566c652465f1672567a5bdba526fb729c10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthUidLogin]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthUidLogin]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthUidLogin]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a9260c718f4a29c4e26b60da98c7787d6ee00f994a048d8e8a2211bc9b8f0c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAkeylessAuthUidLoginOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dataAkeylessAuth.DataAkeylessAuthUidLoginOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6733237593b2839d3bb0efa549d9e2bdbca15f6ccf0504b5e8f907a45d89a513)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAccessId")
    def reset_access_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessId", []))

    @builtins.property
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="uidTokenInput")
    def uid_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uidTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dac9117574e9825923f1952aeb871af39b29512d5f79727107d29f03913d6b19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="uidToken")
    def uid_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uidToken"))

    @uid_token.setter
    def uid_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36524c5066b8793d88e0d09946ab73c652da83ea2230aae18ef6d64ac93aa5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uidToken", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthUidLogin]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthUidLogin]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthUidLogin]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6ceeee5b8ce76877014d990d5db6d6f0729eaa360b5f9dbd66913639e31ffaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAkeylessAuth",
    "DataAkeylessAuthApiKeyLogin",
    "DataAkeylessAuthApiKeyLoginList",
    "DataAkeylessAuthApiKeyLoginOutputReference",
    "DataAkeylessAuthAwsIamLogin",
    "DataAkeylessAuthAwsIamLoginList",
    "DataAkeylessAuthAwsIamLoginOutputReference",
    "DataAkeylessAuthAzureAdLogin",
    "DataAkeylessAuthAzureAdLoginList",
    "DataAkeylessAuthAzureAdLoginOutputReference",
    "DataAkeylessAuthCertLogin",
    "DataAkeylessAuthCertLoginList",
    "DataAkeylessAuthCertLoginOutputReference",
    "DataAkeylessAuthConfig",
    "DataAkeylessAuthEmailLogin",
    "DataAkeylessAuthEmailLoginList",
    "DataAkeylessAuthEmailLoginOutputReference",
    "DataAkeylessAuthGcpLogin",
    "DataAkeylessAuthGcpLoginList",
    "DataAkeylessAuthGcpLoginOutputReference",
    "DataAkeylessAuthJwtLogin",
    "DataAkeylessAuthJwtLoginList",
    "DataAkeylessAuthJwtLoginOutputReference",
    "DataAkeylessAuthUidLogin",
    "DataAkeylessAuthUidLoginList",
    "DataAkeylessAuthUidLoginOutputReference",
]

publication.publish()

def _typecheckingstub__7298ab4ef3e9bb1a091ca027f1512e301f846a47813dd1aa67c06c9b7203f033(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthApiKeyLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAwsIamLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAzureAdLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthCertLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthEmailLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthGcpLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthJwtLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthUidLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__9f21f1b2664af080a7bfc29ec1400924b2ff40aba166fcc5a2510ca755809758(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a484d072358ecd400e2bebe77906dec109e85168983ee81dc9c329a8e0b1d2f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthApiKeyLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4bbf6b692abce839070db4d89f87f0bff3eb8646344ba492fd8c6d32eac51b5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAwsIamLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9f3adff41d9658bed8f1b5d9d0b3314939bb7bec0eb17bbd9df6c54a84c635(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAzureAdLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea674be7961be5f446e5c10b32657dd19cb851bafc67c73c0bbf3c8e046730ea(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthCertLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0efed4e53c1ea04ca2e2b68a4bc7be1b8d98cdaaab49d31b9adcf8728a1fa547(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthEmailLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bf49ca1003318f0bc67785e5ddf40fd660f6ea2aa90954c9e56371e85ae72b0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthGcpLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb38c709e3aaeeab7f88026504e9b6d92b89f548549ea92309aa59d67e1253bf(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthJwtLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48921f2a567a2203c40dc1de40d5d8a547d86714bae9e5bebc00394a461b65cb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthUidLogin, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f3699903aba51a787ec909aae11b8a630aff5c8aa336c30a7bfc29bf992e68d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3354f26069c1bff5d65f08c2ba881c08400eb9b86e7fb39ee374c65a252de26a(
    *,
    access_id: builtins.str,
    access_key: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70b67173a65e4a410909f102a72a013ce2e6eaebe26a5e5539cfa067a9a1ca92(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b783b35b6ee3d262422d943bc4bada512e8711905ec0f66ef0487a73c70a9dc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d0bd6f070ab40f696b7a22a0c3c9206a2e473168cf4d34835e46d8b412be734(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfe163cbacb41ebd0960be510e54cf1ca746184471f6f8735e223c6475969e01(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb316e45628e361214db6b96961635b90a8e2a8ff8a2c67fa195f9b5118df878(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b67eb4e3d1f034ef84c6c2a47edea923edfae51353d8d8235449b3488b776f27(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthApiKeyLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dfb9296459c80ec64b7f74ff283e0ed049ee431e37f9540669c523724a264ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8155265e1c25351cb8ab6849c9c6405b80bcb4d7514b17095e38a628136d801c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f52603dbfb2df56fc0b4ef66531c3af4c484d66ae4c92811804be426ec290a44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b951b2f2dfbe401c04108cb4d2a76815f0884c220cead0efececc6e8546ad4ea(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthApiKeyLogin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12f11e15b3d4e1f268260721e0bb8c2558947fb576fcdabdf1f84b13e2dec07f(
    *,
    access_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95384a78d733cef114cc50ed9cf13c0d839ea8a60ded43c4a3841cd20d1023b8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43e95f072588e8da00e19479c72c4d7382cdf15d1401699ea221b48a5a1c83be(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4afb1b3855ea47589a54fd6ca2e2c533172a69f5c97d1a6032d76931ab4140b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28d1b10087b89f1e556f3d77e60c2658ae8af65d896f35206337faf6a690dee2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57cc1e218dd753411921e2606a02aa9f01c838e2c35d2e6bd7391aed66f70fa4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5797ebfa1baebb1f06199cbbc49a6ae73d25aaad3a32503fb332f94b9f011c60(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAwsIamLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36bfd631a70687f36cf3ac022b086e74bba12423b236ebf51bd961dccf5c3175(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38977924b9b84495abee8563b8cb0c80a0bfea5e1de043e1665898c70fd3a224(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b104859e997986e7802f1fdf602d4c2f44d47fc5b3e25afb343cf9d51a8c975e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAwsIamLogin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dfc161b0dedf328ffbc5cf678f37929d3b48bca2901b33a01b2206cfc72d562(
    *,
    access_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e094b8c098ac2831718e5b400e5cea95038c61627ba68156ce9f46af9c9442(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91b7ba43d87eefd3d612e555a56d274d0152210c98d1efe8e9b64fb7128a68d1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be92dc2913d21cb68d4bec4ff8e149f8997396e1daf6064cac23061a2a301a0c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a25d0b5ec74f012e27446eda3dd528e56a4f428ec165e315ffa3f201f70f7ed7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246533fb8b32fb64fb70248bfe64fe50319318b02f83d6ee0f997f75aa3808d7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__491436b5c8ddc9735a2e34eb54cbe1f0b7a424f4aa0b67adb01ec6fa6758d27f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthAzureAdLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf9607a7a9c4ab0e2df8c675c4a4e717eb1b2497b66e2d7621bcb2c8d6448a86(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__852dca0229f42226a8832af346f103f468a831f58f225163cce57cea094f5455(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aaba41db53741bce08f01fbab47dd52fc8755661be67c6a97ee26bc1432c89e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthAzureAdLogin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80a72db72549b7685d437cff57d63831e3678282d91d30eabf8b6de386521113(
    *,
    access_id: builtins.str,
    cert_data: typing.Optional[builtins.str] = None,
    cert_file_name: typing.Optional[builtins.str] = None,
    key_data: typing.Optional[builtins.str] = None,
    key_file_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f683772cf616599f258e20105c0a6b13dc1fd33799e60e17e34fbb41636470(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f917be5fe48cda885bf9c406a2192c39515f995aa64c8b53676f4115840cdacb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34aaa76ffca92c0839de513527fb30610b4deff9f0632b5bcf0cea2cc8149b79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6626aaf8fc354617de952f9de8ecafbaf52fa575e4374bd62b41efa8b53bb9e7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa8aaceda54ee395af5c724a5b11345500664f384618658509c303cb2636f54e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__792bf688675ccc055b75c3c62f063ce929375b3005b7683d6ab74d4a46d100f3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthCertLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07312dbf71c7ccda634d5c42bca4985b616f10778566812e330d2bbdbb01a542(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__958e7559636db0e1f1039a614ee4f72f2d53e4eb264104c04871962b7145ca7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b35f1b0d4636f3cddb27227f60fa2a0a844fb827b62d938a08399dc7ca139efa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2236af54ba5368214f797a553e84735d7f2546b7726b04b1125815d876b74974(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e98261161216c2c5e8e87ef7ff28f1f2af908705c209986032e8731c3605c166(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cf1812ef747318863f649e8f7c0df99828ffd42ce80fe59e5029115fc662c72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4f312c1ef002e520b15add3bd364d37925c079c8aa6a9035a0bcbafb7a5df97(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthCertLogin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eb0e7588d9fa550f79cfb161fe36b7ca67dc3acebba6838ba26256c2aedb091(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_key_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthApiKeyLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_iam_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAwsIamLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_ad_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthAzureAdLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cert_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthCertLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    email_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthEmailLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    gcp_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthGcpLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    jwt_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthJwtLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
    uid_login: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAkeylessAuthUidLogin, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64efbf48d114457193ebb98dc9cbd7f91d3ffce3731abcb5f7ae1622d887051c(
    *,
    admin_email: builtins.str,
    admin_password: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3870b5fd60723498e64b3495e92b68be6dd01c48682256c8b42e4e8b3e28909b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fb3015857020dac89c7c1be7a83abf2e509954d1d06304e2a8381591fba219b(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61d4bd83bdf9ad8feef77105227e8a8fd3272416f7c1988bf80977ba7daacd0c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d6a3ab9de4291c0b1882751083104b30a400901820a19c635c4d64810e5bcf0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48ec0020fdc0b87f0f4d58613cf2d41b8120d71dff70a3b1f7d54438dd3533f4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30027d9bce148ba2b34c16fa88944fa45aa0fd4ee43cb62eabb24af3f1dc09ca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthEmailLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57951e0ed64ca1b09ce939ea7a85ba94ecbdcb60ce8b8d2b89ccc3a37aacc12e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98c52ca9eab9c8f0fd6ac3b09f6a20f082364dc7285a96af5b8c2ddef6388b28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab0b3e1ed68adc2420ecc29a54c463c3df181230a0e2cc80bca6425f12f4cd96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e45aee314ba3d11631f02050a0bc4ebe80f7f22dbd2fb78ea0544fee80d3737(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthEmailLogin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a47d7bab5420732084146c3e3a7f282fcc84adc410506d7667f50558501a7f68(
    *,
    access_id: builtins.str,
    audience: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47733dbca838ba5b0103c435c5c0e3a4d278aaa28e38e611d66f4478b30fe17e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9a96925870df5a42f526312a9235b387b7289a45d07655e81f979109ad52f53(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba9e3520b3e09cf33be8dc193336410d532dce01121da59dccf69844871f4a31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d428cb149cefe17b69627301e2ad268fe2550a7946d158af8330930a5743a01c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fadd776dc7337deeae13fbdfd16fe20ffa36dff7d1f0f60d345e60804dff6822(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f49b708b750a079eb5504777d3804b47bc764672bce0e6d673cdc4c8b1dbc42d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthGcpLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47f366a60289d5ed47ab9d4ec5fdc81f59038843b4077a53c86b8500da4a6eb8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abdf7181db64cd7cc4ec13e9a8cffd33462326b69c162fe628a1ce729eccbb3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bcef6bf8693856aac4c215f772f48b0f2304aea6930cc15ce4f806171be3eac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f743bb01d913f633cba6d3b6b42a8d3473397f1a239b42b7b4ea3b0d19b557a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthGcpLogin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d91ff787ec556ff7136f5a74510c4e2b7dd13a07d88a228d92c070af72caf78(
    *,
    access_id: builtins.str,
    jwt: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19deb411573b9c6b7bd91047160b58ec8f0f137aa8817692ab637b3a2d74e935(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99b8cbbf9035d9af589684843a13ffc8e724f55c84f145bef184c41a92f06164(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77c39d4e0ab799d4eb214b743eeb2c2c102059017b65f501a29a54511e2124f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9843edbb1c50e85e9cfd823407f68d9ba3af014b85889dea3fc8c4fac335dc42(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e094a8eb7394dc849416fc9993c69c0722e7f130ccbbaf5c335753d6bb968782(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dd3aebda9396182107a90508a7172c81619f363864fd94c4871da870da648ae(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthJwtLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__852a30b97c346bc07bdc0e4abe073950ecce59251fe98603dedbcd0c580946ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__007bc14a8b2b2b1503597fe9f9f3ffbc65d8322b4af1ee249ef218baa8ba5c63(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bccbdbfe5b9c400f3ba4dab9c49c43ceaeb50649b1aa654a7eb0199de86c423(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ca952d5e29f84c79365d041a0597e562f003a4ac3aa6979a4257e6f9b845e26(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthJwtLogin]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05b42ce646de641f35ca8ec9c3059fc862b586388255f32ff28bb225853ebeb7(
    *,
    uid_token: builtins.str,
    access_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8843ad2377a20272a90392ff5cea1d1cbb8d2da1000fb75aa8142c663be55ef7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de0a71d8ae4cf388a73dd091ba695ac870354e2c733373a1f33a594e7621916e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b9ca762811fa92485ed1179ce24573112eae93d5a6255a6f88189601ca1b8f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f604ce996d99aa1a2256757d4dee42f7dfc4d30d65c41ca563c5cc672dcff77c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dce18985e2fe2a637622ee080dabc566c652465f1672567a5bdba526fb729c10(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a9260c718f4a29c4e26b60da98c7787d6ee00f994a048d8e8a2211bc9b8f0c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAkeylessAuthUidLogin]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6733237593b2839d3bb0efa549d9e2bdbca15f6ccf0504b5e8f907a45d89a513(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dac9117574e9825923f1952aeb871af39b29512d5f79727107d29f03913d6b19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36524c5066b8793d88e0d09946ab73c652da83ea2230aae18ef6d64ac93aa5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6ceeee5b8ce76877014d990d5db6d6f0729eaa360b5f9dbd66913639e31ffaa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAkeylessAuthUidLogin]],
) -> None:
    """Type checking stubs"""
    pass
