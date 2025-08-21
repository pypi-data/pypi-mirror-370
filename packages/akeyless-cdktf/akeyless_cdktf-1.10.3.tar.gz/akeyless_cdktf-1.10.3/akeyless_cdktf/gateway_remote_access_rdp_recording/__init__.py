'''
# `akeyless_gateway_remote_access_rdp_recording`

Refer to the Terraform Registry for docs: [`akeyless_gateway_remote_access_rdp_recording`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording).
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


class GatewayRemoteAccessRdpRecording(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.gatewayRemoteAccessRdpRecording.GatewayRemoteAccessRdpRecording",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording akeyless_gateway_remote_access_rdp_recording}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        aws_storage_access_key_id: typing.Optional[builtins.str] = None,
        aws_storage_bucket_name: typing.Optional[builtins.str] = None,
        aws_storage_bucket_prefix: typing.Optional[builtins.str] = None,
        aws_storage_region: typing.Optional[builtins.str] = None,
        aws_storage_secret_access_key: typing.Optional[builtins.str] = None,
        azure_storage_account_name: typing.Optional[builtins.str] = None,
        azure_storage_client_id: typing.Optional[builtins.str] = None,
        azure_storage_client_secret: typing.Optional[builtins.str] = None,
        azure_storage_container_name: typing.Optional[builtins.str] = None,
        azure_storage_tenant_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        rdp_session_recording: typing.Optional[builtins.str] = None,
        rdp_session_storage: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording akeyless_gateway_remote_access_rdp_recording} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param aws_storage_access_key_id: AWS access key id. For more information refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_access_key_id GatewayRemoteAccessRdpRecording#aws_storage_access_key_id}
        :param aws_storage_bucket_name: The AWS bucket name. For more information refer to https://docs.aws.amazon.com/s3/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_bucket_name GatewayRemoteAccessRdpRecording#aws_storage_bucket_name}
        :param aws_storage_bucket_prefix: The folder name in S3 bucket. For more information refer to https://docs.aws.amazon.com/s3/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_bucket_prefix GatewayRemoteAccessRdpRecording#aws_storage_bucket_prefix}
        :param aws_storage_region: The region where the storage is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_region GatewayRemoteAccessRdpRecording#aws_storage_region}
        :param aws_storage_secret_access_key: AWS secret access key. For more information refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_secret_access_key GatewayRemoteAccessRdpRecording#aws_storage_secret_access_key}
        :param azure_storage_account_name: Azure account name. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_account_name GatewayRemoteAccessRdpRecording#azure_storage_account_name}
        :param azure_storage_client_id: Azure client id. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-get-info?tabs=portal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_client_id GatewayRemoteAccessRdpRecording#azure_storage_client_id}
        :param azure_storage_client_secret: Azure client secret. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-get-info?tabs=portal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_client_secret GatewayRemoteAccessRdpRecording#azure_storage_client_secret}
        :param azure_storage_container_name: Azure container name. For more information refer to https://learn.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_container_name GatewayRemoteAccessRdpRecording#azure_storage_container_name}
        :param azure_storage_tenant_id: Azure tenant id. For more information refer to https://learn.microsoft.com/en-us/entra/fundamentals/how-to-find-tenant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_tenant_id GatewayRemoteAccessRdpRecording#azure_storage_tenant_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#id GatewayRemoteAccessRdpRecording#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rdp_session_recording: Enable recording of rdp session [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#rdp_session_recording GatewayRemoteAccessRdpRecording#rdp_session_recording}
        :param rdp_session_storage: Rdp session recording storage destination [local/aws/azure]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#rdp_session_storage GatewayRemoteAccessRdpRecording#rdp_session_storage}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32f1ef8c13ded1e812cc94362faf87f8fe573e912c600196c4a7dc7305ef7c36)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayRemoteAccessRdpRecordingConfig(
            aws_storage_access_key_id=aws_storage_access_key_id,
            aws_storage_bucket_name=aws_storage_bucket_name,
            aws_storage_bucket_prefix=aws_storage_bucket_prefix,
            aws_storage_region=aws_storage_region,
            aws_storage_secret_access_key=aws_storage_secret_access_key,
            azure_storage_account_name=azure_storage_account_name,
            azure_storage_client_id=azure_storage_client_id,
            azure_storage_client_secret=azure_storage_client_secret,
            azure_storage_container_name=azure_storage_container_name,
            azure_storage_tenant_id=azure_storage_tenant_id,
            id=id,
            rdp_session_recording=rdp_session_recording,
            rdp_session_storage=rdp_session_storage,
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
        '''Generates CDKTF code for importing a GatewayRemoteAccessRdpRecording resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayRemoteAccessRdpRecording to import.
        :param import_from_id: The id of the existing GatewayRemoteAccessRdpRecording that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayRemoteAccessRdpRecording to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d85ac904ac2aa20b85276d6e3a52ed43fbcf151096ab2637107ac0e8b400d286)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAwsStorageAccessKeyId")
    def reset_aws_storage_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsStorageAccessKeyId", []))

    @jsii.member(jsii_name="resetAwsStorageBucketName")
    def reset_aws_storage_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsStorageBucketName", []))

    @jsii.member(jsii_name="resetAwsStorageBucketPrefix")
    def reset_aws_storage_bucket_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsStorageBucketPrefix", []))

    @jsii.member(jsii_name="resetAwsStorageRegion")
    def reset_aws_storage_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsStorageRegion", []))

    @jsii.member(jsii_name="resetAwsStorageSecretAccessKey")
    def reset_aws_storage_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsStorageSecretAccessKey", []))

    @jsii.member(jsii_name="resetAzureStorageAccountName")
    def reset_azure_storage_account_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageAccountName", []))

    @jsii.member(jsii_name="resetAzureStorageClientId")
    def reset_azure_storage_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageClientId", []))

    @jsii.member(jsii_name="resetAzureStorageClientSecret")
    def reset_azure_storage_client_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageClientSecret", []))

    @jsii.member(jsii_name="resetAzureStorageContainerName")
    def reset_azure_storage_container_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageContainerName", []))

    @jsii.member(jsii_name="resetAzureStorageTenantId")
    def reset_azure_storage_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureStorageTenantId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRdpSessionRecording")
    def reset_rdp_session_recording(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpSessionRecording", []))

    @jsii.member(jsii_name="resetRdpSessionStorage")
    def reset_rdp_session_storage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRdpSessionStorage", []))

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
    @jsii.member(jsii_name="awsStorageAccessKeyIdInput")
    def aws_storage_access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsStorageAccessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="awsStorageBucketNameInput")
    def aws_storage_bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsStorageBucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="awsStorageBucketPrefixInput")
    def aws_storage_bucket_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsStorageBucketPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="awsStorageRegionInput")
    def aws_storage_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsStorageRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="awsStorageSecretAccessKeyInput")
    def aws_storage_secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsStorageSecretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageAccountNameInput")
    def azure_storage_account_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageAccountNameInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageClientIdInput")
    def azure_storage_client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageClientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageClientSecretInput")
    def azure_storage_client_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageClientSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageContainerNameInput")
    def azure_storage_container_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageContainerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="azureStorageTenantIdInput")
    def azure_storage_tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureStorageTenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpSessionRecordingInput")
    def rdp_session_recording_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpSessionRecordingInput"))

    @builtins.property
    @jsii.member(jsii_name="rdpSessionStorageInput")
    def rdp_session_storage_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rdpSessionStorageInput"))

    @builtins.property
    @jsii.member(jsii_name="awsStorageAccessKeyId")
    def aws_storage_access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsStorageAccessKeyId"))

    @aws_storage_access_key_id.setter
    def aws_storage_access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b20dbaa33841fe92302d7c8c8fe133bc5edb2b30fa10e971ced13069fbb0e2da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsStorageAccessKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="awsStorageBucketName")
    def aws_storage_bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsStorageBucketName"))

    @aws_storage_bucket_name.setter
    def aws_storage_bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b41703a7731b7998001a9ab81173ebb31fa74de3ab9ef045097e6a96690d8f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsStorageBucketName", value)

    @builtins.property
    @jsii.member(jsii_name="awsStorageBucketPrefix")
    def aws_storage_bucket_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsStorageBucketPrefix"))

    @aws_storage_bucket_prefix.setter
    def aws_storage_bucket_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ce91859d70db04af3bb81a1751c7f2434121d5dfd3945643cf70e01940ad0d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsStorageBucketPrefix", value)

    @builtins.property
    @jsii.member(jsii_name="awsStorageRegion")
    def aws_storage_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsStorageRegion"))

    @aws_storage_region.setter
    def aws_storage_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1e1e76546139502796d62694a4c99476af52eb3480d3577449fdf06c0867943)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsStorageRegion", value)

    @builtins.property
    @jsii.member(jsii_name="awsStorageSecretAccessKey")
    def aws_storage_secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsStorageSecretAccessKey"))

    @aws_storage_secret_access_key.setter
    def aws_storage_secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac9880da22fa5f9efa8f8aaf2769a3e63721329f159ab58420ee501bd82ce5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsStorageSecretAccessKey", value)

    @builtins.property
    @jsii.member(jsii_name="azureStorageAccountName")
    def azure_storage_account_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageAccountName"))

    @azure_storage_account_name.setter
    def azure_storage_account_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb805b0334b1aa2134ffef8cf454e3e9080784bdf0b111c10d6f6008556fda0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageAccountName", value)

    @builtins.property
    @jsii.member(jsii_name="azureStorageClientId")
    def azure_storage_client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageClientId"))

    @azure_storage_client_id.setter
    def azure_storage_client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82011705160d1c22eee8c778d549e251db3f55e77f69970a69f38a087aa1d5ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageClientId", value)

    @builtins.property
    @jsii.member(jsii_name="azureStorageClientSecret")
    def azure_storage_client_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageClientSecret"))

    @azure_storage_client_secret.setter
    def azure_storage_client_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__007895ad2b1d3d63d7733a4e4b3f6f8c371b7561e60753ec1e8f7edd6dcddb2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageClientSecret", value)

    @builtins.property
    @jsii.member(jsii_name="azureStorageContainerName")
    def azure_storage_container_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageContainerName"))

    @azure_storage_container_name.setter
    def azure_storage_container_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23706e64d29b8c2af108cdad1fc7a4c58c3103c3817866cdbc0ce951348e4f3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageContainerName", value)

    @builtins.property
    @jsii.member(jsii_name="azureStorageTenantId")
    def azure_storage_tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureStorageTenantId"))

    @azure_storage_tenant_id.setter
    def azure_storage_tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cea21acef7500cdb3d4646cb7924cd74ecf25c7f802fe5476a8e32938667cfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureStorageTenantId", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e1f3d84b5686a65d3f06f6ba20478ffa4af1aba9db53249111d59e8b85c66c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="rdpSessionRecording")
    def rdp_session_recording(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpSessionRecording"))

    @rdp_session_recording.setter
    def rdp_session_recording(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd4bd4f5e45d9e1d6cab04fffcc2d7434f1fc6e6b5e6c8f3c19463dbe1d7b7de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpSessionRecording", value)

    @builtins.property
    @jsii.member(jsii_name="rdpSessionStorage")
    def rdp_session_storage(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rdpSessionStorage"))

    @rdp_session_storage.setter
    def rdp_session_storage(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db9be35e48fb388f9387ce2d0b143c9d9a4b9bd8615d7463431d38826ece201d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rdpSessionStorage", value)


@jsii.data_type(
    jsii_type="akeyless.gatewayRemoteAccessRdpRecording.GatewayRemoteAccessRdpRecordingConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "aws_storage_access_key_id": "awsStorageAccessKeyId",
        "aws_storage_bucket_name": "awsStorageBucketName",
        "aws_storage_bucket_prefix": "awsStorageBucketPrefix",
        "aws_storage_region": "awsStorageRegion",
        "aws_storage_secret_access_key": "awsStorageSecretAccessKey",
        "azure_storage_account_name": "azureStorageAccountName",
        "azure_storage_client_id": "azureStorageClientId",
        "azure_storage_client_secret": "azureStorageClientSecret",
        "azure_storage_container_name": "azureStorageContainerName",
        "azure_storage_tenant_id": "azureStorageTenantId",
        "id": "id",
        "rdp_session_recording": "rdpSessionRecording",
        "rdp_session_storage": "rdpSessionStorage",
    },
)
class GatewayRemoteAccessRdpRecordingConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        aws_storage_access_key_id: typing.Optional[builtins.str] = None,
        aws_storage_bucket_name: typing.Optional[builtins.str] = None,
        aws_storage_bucket_prefix: typing.Optional[builtins.str] = None,
        aws_storage_region: typing.Optional[builtins.str] = None,
        aws_storage_secret_access_key: typing.Optional[builtins.str] = None,
        azure_storage_account_name: typing.Optional[builtins.str] = None,
        azure_storage_client_id: typing.Optional[builtins.str] = None,
        azure_storage_client_secret: typing.Optional[builtins.str] = None,
        azure_storage_container_name: typing.Optional[builtins.str] = None,
        azure_storage_tenant_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        rdp_session_recording: typing.Optional[builtins.str] = None,
        rdp_session_storage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param aws_storage_access_key_id: AWS access key id. For more information refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_access_key_id GatewayRemoteAccessRdpRecording#aws_storage_access_key_id}
        :param aws_storage_bucket_name: The AWS bucket name. For more information refer to https://docs.aws.amazon.com/s3/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_bucket_name GatewayRemoteAccessRdpRecording#aws_storage_bucket_name}
        :param aws_storage_bucket_prefix: The folder name in S3 bucket. For more information refer to https://docs.aws.amazon.com/s3/. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_bucket_prefix GatewayRemoteAccessRdpRecording#aws_storage_bucket_prefix}
        :param aws_storage_region: The region where the storage is located. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_region GatewayRemoteAccessRdpRecording#aws_storage_region}
        :param aws_storage_secret_access_key: AWS secret access key. For more information refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_secret_access_key GatewayRemoteAccessRdpRecording#aws_storage_secret_access_key}
        :param azure_storage_account_name: Azure account name. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_account_name GatewayRemoteAccessRdpRecording#azure_storage_account_name}
        :param azure_storage_client_id: Azure client id. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-get-info?tabs=portal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_client_id GatewayRemoteAccessRdpRecording#azure_storage_client_id}
        :param azure_storage_client_secret: Azure client secret. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-get-info?tabs=portal. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_client_secret GatewayRemoteAccessRdpRecording#azure_storage_client_secret}
        :param azure_storage_container_name: Azure container name. For more information refer to https://learn.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_container_name GatewayRemoteAccessRdpRecording#azure_storage_container_name}
        :param azure_storage_tenant_id: Azure tenant id. For more information refer to https://learn.microsoft.com/en-us/entra/fundamentals/how-to-find-tenant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_tenant_id GatewayRemoteAccessRdpRecording#azure_storage_tenant_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#id GatewayRemoteAccessRdpRecording#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param rdp_session_recording: Enable recording of rdp session [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#rdp_session_recording GatewayRemoteAccessRdpRecording#rdp_session_recording}
        :param rdp_session_storage: Rdp session recording storage destination [local/aws/azure]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#rdp_session_storage GatewayRemoteAccessRdpRecording#rdp_session_storage}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2913e92a4296b7c3c308f37728734952158c56c97acfc5399793f7d628a35d5)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument aws_storage_access_key_id", value=aws_storage_access_key_id, expected_type=type_hints["aws_storage_access_key_id"])
            check_type(argname="argument aws_storage_bucket_name", value=aws_storage_bucket_name, expected_type=type_hints["aws_storage_bucket_name"])
            check_type(argname="argument aws_storage_bucket_prefix", value=aws_storage_bucket_prefix, expected_type=type_hints["aws_storage_bucket_prefix"])
            check_type(argname="argument aws_storage_region", value=aws_storage_region, expected_type=type_hints["aws_storage_region"])
            check_type(argname="argument aws_storage_secret_access_key", value=aws_storage_secret_access_key, expected_type=type_hints["aws_storage_secret_access_key"])
            check_type(argname="argument azure_storage_account_name", value=azure_storage_account_name, expected_type=type_hints["azure_storage_account_name"])
            check_type(argname="argument azure_storage_client_id", value=azure_storage_client_id, expected_type=type_hints["azure_storage_client_id"])
            check_type(argname="argument azure_storage_client_secret", value=azure_storage_client_secret, expected_type=type_hints["azure_storage_client_secret"])
            check_type(argname="argument azure_storage_container_name", value=azure_storage_container_name, expected_type=type_hints["azure_storage_container_name"])
            check_type(argname="argument azure_storage_tenant_id", value=azure_storage_tenant_id, expected_type=type_hints["azure_storage_tenant_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument rdp_session_recording", value=rdp_session_recording, expected_type=type_hints["rdp_session_recording"])
            check_type(argname="argument rdp_session_storage", value=rdp_session_storage, expected_type=type_hints["rdp_session_storage"])
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
        if aws_storage_access_key_id is not None:
            self._values["aws_storage_access_key_id"] = aws_storage_access_key_id
        if aws_storage_bucket_name is not None:
            self._values["aws_storage_bucket_name"] = aws_storage_bucket_name
        if aws_storage_bucket_prefix is not None:
            self._values["aws_storage_bucket_prefix"] = aws_storage_bucket_prefix
        if aws_storage_region is not None:
            self._values["aws_storage_region"] = aws_storage_region
        if aws_storage_secret_access_key is not None:
            self._values["aws_storage_secret_access_key"] = aws_storage_secret_access_key
        if azure_storage_account_name is not None:
            self._values["azure_storage_account_name"] = azure_storage_account_name
        if azure_storage_client_id is not None:
            self._values["azure_storage_client_id"] = azure_storage_client_id
        if azure_storage_client_secret is not None:
            self._values["azure_storage_client_secret"] = azure_storage_client_secret
        if azure_storage_container_name is not None:
            self._values["azure_storage_container_name"] = azure_storage_container_name
        if azure_storage_tenant_id is not None:
            self._values["azure_storage_tenant_id"] = azure_storage_tenant_id
        if id is not None:
            self._values["id"] = id
        if rdp_session_recording is not None:
            self._values["rdp_session_recording"] = rdp_session_recording
        if rdp_session_storage is not None:
            self._values["rdp_session_storage"] = rdp_session_storage

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
    def aws_storage_access_key_id(self) -> typing.Optional[builtins.str]:
        '''AWS access key id. For more information refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_access_key_id GatewayRemoteAccessRdpRecording#aws_storage_access_key_id}
        '''
        result = self._values.get("aws_storage_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_storage_bucket_name(self) -> typing.Optional[builtins.str]:
        '''The AWS bucket name. For more information refer to https://docs.aws.amazon.com/s3/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_bucket_name GatewayRemoteAccessRdpRecording#aws_storage_bucket_name}
        '''
        result = self._values.get("aws_storage_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_storage_bucket_prefix(self) -> typing.Optional[builtins.str]:
        '''The folder name in S3 bucket. For more information refer to https://docs.aws.amazon.com/s3/.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_bucket_prefix GatewayRemoteAccessRdpRecording#aws_storage_bucket_prefix}
        '''
        result = self._values.get("aws_storage_bucket_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_storage_region(self) -> typing.Optional[builtins.str]:
        '''The region where the storage is located.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_region GatewayRemoteAccessRdpRecording#aws_storage_region}
        '''
        result = self._values.get("aws_storage_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_storage_secret_access_key(self) -> typing.Optional[builtins.str]:
        '''AWS secret access key. For more information refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#aws_storage_secret_access_key GatewayRemoteAccessRdpRecording#aws_storage_secret_access_key}
        '''
        result = self._values.get("aws_storage_secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_account_name(self) -> typing.Optional[builtins.str]:
        '''Azure account name. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-overview.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_account_name GatewayRemoteAccessRdpRecording#azure_storage_account_name}
        '''
        result = self._values.get("azure_storage_account_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_client_id(self) -> typing.Optional[builtins.str]:
        '''Azure client id. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-get-info?tabs=portal.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_client_id GatewayRemoteAccessRdpRecording#azure_storage_client_id}
        '''
        result = self._values.get("azure_storage_client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_client_secret(self) -> typing.Optional[builtins.str]:
        '''Azure client secret. For more information refer to https://learn.microsoft.com/en-us/azure/storage/common/storage-account-get-info?tabs=portal.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_client_secret GatewayRemoteAccessRdpRecording#azure_storage_client_secret}
        '''
        result = self._values.get("azure_storage_client_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_container_name(self) -> typing.Optional[builtins.str]:
        '''Azure container name. For more information refer to https://learn.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_container_name GatewayRemoteAccessRdpRecording#azure_storage_container_name}
        '''
        result = self._values.get("azure_storage_container_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_storage_tenant_id(self) -> typing.Optional[builtins.str]:
        '''Azure tenant id. For more information refer to https://learn.microsoft.com/en-us/entra/fundamentals/how-to-find-tenant.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#azure_storage_tenant_id GatewayRemoteAccessRdpRecording#azure_storage_tenant_id}
        '''
        result = self._values.get("azure_storage_tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#id GatewayRemoteAccessRdpRecording#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_session_recording(self) -> typing.Optional[builtins.str]:
        '''Enable recording of rdp session [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#rdp_session_recording GatewayRemoteAccessRdpRecording#rdp_session_recording}
        '''
        result = self._values.get("rdp_session_recording")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rdp_session_storage(self) -> typing.Optional[builtins.str]:
        '''Rdp session recording storage destination [local/aws/azure].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_remote_access_rdp_recording#rdp_session_storage GatewayRemoteAccessRdpRecording#rdp_session_storage}
        '''
        result = self._values.get("rdp_session_storage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayRemoteAccessRdpRecordingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GatewayRemoteAccessRdpRecording",
    "GatewayRemoteAccessRdpRecordingConfig",
]

publication.publish()

def _typecheckingstub__32f1ef8c13ded1e812cc94362faf87f8fe573e912c600196c4a7dc7305ef7c36(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    aws_storage_access_key_id: typing.Optional[builtins.str] = None,
    aws_storage_bucket_name: typing.Optional[builtins.str] = None,
    aws_storage_bucket_prefix: typing.Optional[builtins.str] = None,
    aws_storage_region: typing.Optional[builtins.str] = None,
    aws_storage_secret_access_key: typing.Optional[builtins.str] = None,
    azure_storage_account_name: typing.Optional[builtins.str] = None,
    azure_storage_client_id: typing.Optional[builtins.str] = None,
    azure_storage_client_secret: typing.Optional[builtins.str] = None,
    azure_storage_container_name: typing.Optional[builtins.str] = None,
    azure_storage_tenant_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    rdp_session_recording: typing.Optional[builtins.str] = None,
    rdp_session_storage: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__d85ac904ac2aa20b85276d6e3a52ed43fbcf151096ab2637107ac0e8b400d286(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b20dbaa33841fe92302d7c8c8fe133bc5edb2b30fa10e971ced13069fbb0e2da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b41703a7731b7998001a9ab81173ebb31fa74de3ab9ef045097e6a96690d8f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ce91859d70db04af3bb81a1751c7f2434121d5dfd3945643cf70e01940ad0d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1e1e76546139502796d62694a4c99476af52eb3480d3577449fdf06c0867943(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac9880da22fa5f9efa8f8aaf2769a3e63721329f159ab58420ee501bd82ce5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb805b0334b1aa2134ffef8cf454e3e9080784bdf0b111c10d6f6008556fda0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82011705160d1c22eee8c778d549e251db3f55e77f69970a69f38a087aa1d5ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__007895ad2b1d3d63d7733a4e4b3f6f8c371b7561e60753ec1e8f7edd6dcddb2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23706e64d29b8c2af108cdad1fc7a4c58c3103c3817866cdbc0ce951348e4f3d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cea21acef7500cdb3d4646cb7924cd74ecf25c7f802fe5476a8e32938667cfa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e1f3d84b5686a65d3f06f6ba20478ffa4af1aba9db53249111d59e8b85c66c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd4bd4f5e45d9e1d6cab04fffcc2d7434f1fc6e6b5e6c8f3c19463dbe1d7b7de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db9be35e48fb388f9387ce2d0b143c9d9a4b9bd8615d7463431d38826ece201d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2913e92a4296b7c3c308f37728734952158c56c97acfc5399793f7d628a35d5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_storage_access_key_id: typing.Optional[builtins.str] = None,
    aws_storage_bucket_name: typing.Optional[builtins.str] = None,
    aws_storage_bucket_prefix: typing.Optional[builtins.str] = None,
    aws_storage_region: typing.Optional[builtins.str] = None,
    aws_storage_secret_access_key: typing.Optional[builtins.str] = None,
    azure_storage_account_name: typing.Optional[builtins.str] = None,
    azure_storage_client_id: typing.Optional[builtins.str] = None,
    azure_storage_client_secret: typing.Optional[builtins.str] = None,
    azure_storage_container_name: typing.Optional[builtins.str] = None,
    azure_storage_tenant_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    rdp_session_recording: typing.Optional[builtins.str] = None,
    rdp_session_storage: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
