'''
# `akeyless_producer_eks`

Refer to the Terraform Registry for docs: [`akeyless_producer_eks`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks).
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


class ProducerEks(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerEks.ProducerEks",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks akeyless_producer_eks}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        eks_access_key_id: typing.Optional[builtins.str] = None,
        eks_assume_role: typing.Optional[builtins.str] = None,
        eks_cluster_ca_cert: typing.Optional[builtins.str] = None,
        eks_cluster_endpoint: typing.Optional[builtins.str] = None,
        eks_cluster_name: typing.Optional[builtins.str] = None,
        eks_region: typing.Optional[builtins.str] = None,
        eks_secret_access_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks akeyless_producer_eks} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#name ProducerEks#name}
        :param eks_access_key_id: EKS Access Key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_access_key_id ProducerEks#eks_access_key_id}
        :param eks_assume_role: Role ARN. Role to assume when connecting to the EKS cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_assume_role ProducerEks#eks_assume_role}
        :param eks_cluster_ca_cert: EKS Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_ca_cert ProducerEks#eks_cluster_ca_cert}
        :param eks_cluster_endpoint: EKS Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_endpoint ProducerEks#eks_cluster_endpoint}
        :param eks_cluster_name: EKS cluster name. Must match the EKS cluster name you want to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_name ProducerEks#eks_cluster_name}
        :param eks_region: EKS Region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_region ProducerEks#eks_region}
        :param eks_secret_access_key: EKS Secret Access Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_secret_access_key ProducerEks#eks_secret_access_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#id ProducerEks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#producer_encryption_key_name ProducerEks#producer_encryption_key_name}
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_allow_port_forwading ProducerEks#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_bastion_issuer ProducerEks#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_cluster_endpoint ProducerEks#secure_access_cluster_endpoint}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_enable ProducerEks#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_web ProducerEks#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#tags ProducerEks#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#target_name ProducerEks#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#user_ttl ProducerEks#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a98fa389264466243feaead5f475e32e6b8f24801e44c656121f9f0b2aed3e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerEksConfig(
            name=name,
            eks_access_key_id=eks_access_key_id,
            eks_assume_role=eks_assume_role,
            eks_cluster_ca_cert=eks_cluster_ca_cert,
            eks_cluster_endpoint=eks_cluster_endpoint,
            eks_cluster_name=eks_cluster_name,
            eks_region=eks_region,
            eks_secret_access_key=eks_secret_access_key,
            id=id,
            producer_encryption_key_name=producer_encryption_key_name,
            secure_access_allow_port_forwading=secure_access_allow_port_forwading,
            secure_access_bastion_issuer=secure_access_bastion_issuer,
            secure_access_cluster_endpoint=secure_access_cluster_endpoint,
            secure_access_enable=secure_access_enable,
            secure_access_web=secure_access_web,
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
        '''Generates CDKTF code for importing a ProducerEks resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerEks to import.
        :param import_from_id: The id of the existing ProducerEks that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerEks to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42b2947b10b5c7e38ef73de3db85f06dda4aca57b20b16cd91f36acf4aeec141)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetEksAccessKeyId")
    def reset_eks_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksAccessKeyId", []))

    @jsii.member(jsii_name="resetEksAssumeRole")
    def reset_eks_assume_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksAssumeRole", []))

    @jsii.member(jsii_name="resetEksClusterCaCert")
    def reset_eks_cluster_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksClusterCaCert", []))

    @jsii.member(jsii_name="resetEksClusterEndpoint")
    def reset_eks_cluster_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksClusterEndpoint", []))

    @jsii.member(jsii_name="resetEksClusterName")
    def reset_eks_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksClusterName", []))

    @jsii.member(jsii_name="resetEksRegion")
    def reset_eks_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksRegion", []))

    @jsii.member(jsii_name="resetEksSecretAccessKey")
    def reset_eks_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksSecretAccessKey", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

    @jsii.member(jsii_name="resetSecureAccessAllowPortForwading")
    def reset_secure_access_allow_port_forwading(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessAllowPortForwading", []))

    @jsii.member(jsii_name="resetSecureAccessBastionIssuer")
    def reset_secure_access_bastion_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessBastionIssuer", []))

    @jsii.member(jsii_name="resetSecureAccessClusterEndpoint")
    def reset_secure_access_cluster_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessClusterEndpoint", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

    @jsii.member(jsii_name="resetSecureAccessWeb")
    def reset_secure_access_web(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWeb", []))

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
    @jsii.member(jsii_name="eksAccessKeyIdInput")
    def eks_access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksAccessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="eksAssumeRoleInput")
    def eks_assume_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksAssumeRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="eksClusterCaCertInput")
    def eks_cluster_ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksClusterCaCertInput"))

    @builtins.property
    @jsii.member(jsii_name="eksClusterEndpointInput")
    def eks_cluster_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksClusterEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="eksClusterNameInput")
    def eks_cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksClusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="eksRegionInput")
    def eks_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="eksSecretAccessKeyInput")
    def eks_secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksSecretAccessKeyInput"))

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
    @jsii.member(jsii_name="secureAccessAllowPortForwadingInput")
    def secure_access_allow_port_forwading_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessAllowPortForwadingInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuerInput")
    def secure_access_bastion_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessBastionIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessClusterEndpointInput")
    def secure_access_cluster_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessClusterEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

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
    @jsii.member(jsii_name="eksAccessKeyId")
    def eks_access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksAccessKeyId"))

    @eks_access_key_id.setter
    def eks_access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__931af49e6c600538ef30249c5cdbb849182397126789a247cc3d38d71ce2c578)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksAccessKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="eksAssumeRole")
    def eks_assume_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksAssumeRole"))

    @eks_assume_role.setter
    def eks_assume_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__593b52bc60dff97982115489e7cc6143896c3f21818ae6123fd2889b13f6da6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksAssumeRole", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterCaCert")
    def eks_cluster_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterCaCert"))

    @eks_cluster_ca_cert.setter
    def eks_cluster_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__621e03c714ed0f009050f38c73298a588524cee4a7c643105101e3f8faeb9cef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterCaCert", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterEndpoint")
    def eks_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterEndpoint"))

    @eks_cluster_endpoint.setter
    def eks_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b737c3fbfe31a499a4ceedaa646b3d322c3d1d51ce7a494bd5deabb1ceb4c18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterName")
    def eks_cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterName"))

    @eks_cluster_name.setter
    def eks_cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3e0cbbb68a0eaf870e638e954a505a0f55c39d407abfc9056ba9edc4ebef8e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterName", value)

    @builtins.property
    @jsii.member(jsii_name="eksRegion")
    def eks_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksRegion"))

    @eks_region.setter
    def eks_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fb9c2cd644005aa957bad5ce54140aaffd0bd96e8718b3daa0a0eab762508b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksRegion", value)

    @builtins.property
    @jsii.member(jsii_name="eksSecretAccessKey")
    def eks_secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksSecretAccessKey"))

    @eks_secret_access_key.setter
    def eks_secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dec05a2a3d277e2769affb0cbc4e9afaf5592896669d14a2744ce76f25a9466)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksSecretAccessKey", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65ce5a05ad1417b84fa64f0120c67dd3659ce4329c01bfbed0f70550bfb5949a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f85f629a15740a1cec63e1b725cdce0338fcec5585d85ce7d0b0bc5223f2bff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0da0aae53beba0552f3522beadba561d66049d7dc1156c1beb4ce4a18293e198)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessAllowPortForwading")
    def secure_access_allow_port_forwading(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessAllowPortForwading"))

    @secure_access_allow_port_forwading.setter
    def secure_access_allow_port_forwading(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a2f02815271bce5d4fec66f235bb4997ace9dde88650547e7493ff784c0a7ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAllowPortForwading", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eeda846feaa22518e0986aaadcf88af3a8eba4d9a3b1f0da7390a61af55e15d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessClusterEndpoint")
    def secure_access_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessClusterEndpoint"))

    @secure_access_cluster_endpoint.setter
    def secure_access_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb8c6563699b72a23ff709f6a3ba80c6be8ed80b3bc24e8b4e9e60e60b6c95d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfd03b0213ae77cab157c2d2bb7e5e9cb3bc9f83023b143ce603a9872a56f90a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__10f40014084ffd32475950228e3f8c521b77faa91e50a51d1fc518a3ceed52b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72bd628a1636480fc47235bd08f674207b6cfd8532c24eaa20cf9f8fc8860012)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a10f704ed3ca12ddecff7e1fc7cbaf68792c8cd39df8307ee82ff6d02700af8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1fc067f401ec55e8a96a7905ad0862a9f4ffbbd6a948acaa8efcfd3e7ad0862)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerEks.ProducerEksConfig",
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
        "eks_access_key_id": "eksAccessKeyId",
        "eks_assume_role": "eksAssumeRole",
        "eks_cluster_ca_cert": "eksClusterCaCert",
        "eks_cluster_endpoint": "eksClusterEndpoint",
        "eks_cluster_name": "eksClusterName",
        "eks_region": "eksRegion",
        "eks_secret_access_key": "eksSecretAccessKey",
        "id": "id",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "secure_access_allow_port_forwading": "secureAccessAllowPortForwading",
        "secure_access_bastion_issuer": "secureAccessBastionIssuer",
        "secure_access_cluster_endpoint": "secureAccessClusterEndpoint",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_web": "secureAccessWeb",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerEksConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        eks_access_key_id: typing.Optional[builtins.str] = None,
        eks_assume_role: typing.Optional[builtins.str] = None,
        eks_cluster_ca_cert: typing.Optional[builtins.str] = None,
        eks_cluster_endpoint: typing.Optional[builtins.str] = None,
        eks_cluster_name: typing.Optional[builtins.str] = None,
        eks_region: typing.Optional[builtins.str] = None,
        eks_secret_access_key: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#name ProducerEks#name}
        :param eks_access_key_id: EKS Access Key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_access_key_id ProducerEks#eks_access_key_id}
        :param eks_assume_role: Role ARN. Role to assume when connecting to the EKS cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_assume_role ProducerEks#eks_assume_role}
        :param eks_cluster_ca_cert: EKS Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_ca_cert ProducerEks#eks_cluster_ca_cert}
        :param eks_cluster_endpoint: EKS Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_endpoint ProducerEks#eks_cluster_endpoint}
        :param eks_cluster_name: EKS cluster name. Must match the EKS cluster name you want to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_name ProducerEks#eks_cluster_name}
        :param eks_region: EKS Region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_region ProducerEks#eks_region}
        :param eks_secret_access_key: EKS Secret Access Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_secret_access_key ProducerEks#eks_secret_access_key}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#id ProducerEks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#producer_encryption_key_name ProducerEks#producer_encryption_key_name}
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_allow_port_forwading ProducerEks#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_bastion_issuer ProducerEks#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_cluster_endpoint ProducerEks#secure_access_cluster_endpoint}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_enable ProducerEks#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_web ProducerEks#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#tags ProducerEks#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#target_name ProducerEks#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#user_ttl ProducerEks#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__797456c5642d1112419068346020a1a633ab9aa84e7ed8ad9a057b833c92f5c3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument eks_access_key_id", value=eks_access_key_id, expected_type=type_hints["eks_access_key_id"])
            check_type(argname="argument eks_assume_role", value=eks_assume_role, expected_type=type_hints["eks_assume_role"])
            check_type(argname="argument eks_cluster_ca_cert", value=eks_cluster_ca_cert, expected_type=type_hints["eks_cluster_ca_cert"])
            check_type(argname="argument eks_cluster_endpoint", value=eks_cluster_endpoint, expected_type=type_hints["eks_cluster_endpoint"])
            check_type(argname="argument eks_cluster_name", value=eks_cluster_name, expected_type=type_hints["eks_cluster_name"])
            check_type(argname="argument eks_region", value=eks_region, expected_type=type_hints["eks_region"])
            check_type(argname="argument eks_secret_access_key", value=eks_secret_access_key, expected_type=type_hints["eks_secret_access_key"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
            check_type(argname="argument secure_access_allow_port_forwading", value=secure_access_allow_port_forwading, expected_type=type_hints["secure_access_allow_port_forwading"])
            check_type(argname="argument secure_access_bastion_issuer", value=secure_access_bastion_issuer, expected_type=type_hints["secure_access_bastion_issuer"])
            check_type(argname="argument secure_access_cluster_endpoint", value=secure_access_cluster_endpoint, expected_type=type_hints["secure_access_cluster_endpoint"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
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
        if eks_access_key_id is not None:
            self._values["eks_access_key_id"] = eks_access_key_id
        if eks_assume_role is not None:
            self._values["eks_assume_role"] = eks_assume_role
        if eks_cluster_ca_cert is not None:
            self._values["eks_cluster_ca_cert"] = eks_cluster_ca_cert
        if eks_cluster_endpoint is not None:
            self._values["eks_cluster_endpoint"] = eks_cluster_endpoint
        if eks_cluster_name is not None:
            self._values["eks_cluster_name"] = eks_cluster_name
        if eks_region is not None:
            self._values["eks_region"] = eks_region
        if eks_secret_access_key is not None:
            self._values["eks_secret_access_key"] = eks_secret_access_key
        if id is not None:
            self._values["id"] = id
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
        if secure_access_allow_port_forwading is not None:
            self._values["secure_access_allow_port_forwading"] = secure_access_allow_port_forwading
        if secure_access_bastion_issuer is not None:
            self._values["secure_access_bastion_issuer"] = secure_access_bastion_issuer
        if secure_access_cluster_endpoint is not None:
            self._values["secure_access_cluster_endpoint"] = secure_access_cluster_endpoint
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_web is not None:
            self._values["secure_access_web"] = secure_access_web
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#name ProducerEks#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eks_access_key_id(self) -> typing.Optional[builtins.str]:
        '''EKS Access Key ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_access_key_id ProducerEks#eks_access_key_id}
        '''
        result = self._values.get("eks_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_assume_role(self) -> typing.Optional[builtins.str]:
        '''Role ARN. Role to assume when connecting to the EKS cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_assume_role ProducerEks#eks_assume_role}
        '''
        result = self._values.get("eks_assume_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_cluster_ca_cert(self) -> typing.Optional[builtins.str]:
        '''EKS Cluster certificate. Base 64 encoded certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_ca_cert ProducerEks#eks_cluster_ca_cert}
        '''
        result = self._values.get("eks_cluster_ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''EKS Cluster endpoint. https:// , <DNS / IP> of the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_endpoint ProducerEks#eks_cluster_endpoint}
        '''
        result = self._values.get("eks_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_cluster_name(self) -> typing.Optional[builtins.str]:
        '''EKS cluster name. Must match the EKS cluster name you want to connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_cluster_name ProducerEks#eks_cluster_name}
        '''
        result = self._values.get("eks_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_region(self) -> typing.Optional[builtins.str]:
        '''EKS Region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_region ProducerEks#eks_region}
        '''
        result = self._values.get("eks_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_secret_access_key(self) -> typing.Optional[builtins.str]:
        '''EKS Secret Access Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#eks_secret_access_key ProducerEks#eks_secret_access_key}
        '''
        result = self._values.get("eks_secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#id ProducerEks#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#producer_encryption_key_name ProducerEks#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_allow_port_forwading(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Port forwarding while using CLI access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_allow_port_forwading ProducerEks#secure_access_allow_port_forwading}
        '''
        result = self._values.get("secure_access_allow_port_forwading")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_bastion_issuer ProducerEks#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''The K8s cluster endpoint URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_cluster_endpoint ProducerEks#secure_access_cluster_endpoint}
        '''
        result = self._values.get("secure_access_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_enable ProducerEks#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#secure_access_web ProducerEks#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#tags ProducerEks#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#target_name ProducerEks#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_eks#user_ttl ProducerEks#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerEksConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerEks",
    "ProducerEksConfig",
]

publication.publish()

def _typecheckingstub__6a98fa389264466243feaead5f475e32e6b8f24801e44c656121f9f0b2aed3e5(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    eks_access_key_id: typing.Optional[builtins.str] = None,
    eks_assume_role: typing.Optional[builtins.str] = None,
    eks_cluster_ca_cert: typing.Optional[builtins.str] = None,
    eks_cluster_endpoint: typing.Optional[builtins.str] = None,
    eks_cluster_name: typing.Optional[builtins.str] = None,
    eks_region: typing.Optional[builtins.str] = None,
    eks_secret_access_key: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__42b2947b10b5c7e38ef73de3db85f06dda4aca57b20b16cd91f36acf4aeec141(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__931af49e6c600538ef30249c5cdbb849182397126789a247cc3d38d71ce2c578(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__593b52bc60dff97982115489e7cc6143896c3f21818ae6123fd2889b13f6da6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__621e03c714ed0f009050f38c73298a588524cee4a7c643105101e3f8faeb9cef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b737c3fbfe31a499a4ceedaa646b3d322c3d1d51ce7a494bd5deabb1ceb4c18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3e0cbbb68a0eaf870e638e954a505a0f55c39d407abfc9056ba9edc4ebef8e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fb9c2cd644005aa957bad5ce54140aaffd0bd96e8718b3daa0a0eab762508b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dec05a2a3d277e2769affb0cbc4e9afaf5592896669d14a2744ce76f25a9466(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65ce5a05ad1417b84fa64f0120c67dd3659ce4329c01bfbed0f70550bfb5949a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f85f629a15740a1cec63e1b725cdce0338fcec5585d85ce7d0b0bc5223f2bff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0da0aae53beba0552f3522beadba561d66049d7dc1156c1beb4ce4a18293e198(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a2f02815271bce5d4fec66f235bb4997ace9dde88650547e7493ff784c0a7ae(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeda846feaa22518e0986aaadcf88af3a8eba4d9a3b1f0da7390a61af55e15d5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb8c6563699b72a23ff709f6a3ba80c6be8ed80b3bc24e8b4e9e60e60b6c95d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfd03b0213ae77cab157c2d2bb7e5e9cb3bc9f83023b143ce603a9872a56f90a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10f40014084ffd32475950228e3f8c521b77faa91e50a51d1fc518a3ceed52b5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72bd628a1636480fc47235bd08f674207b6cfd8532c24eaa20cf9f8fc8860012(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a10f704ed3ca12ddecff7e1fc7cbaf68792c8cd39df8307ee82ff6d02700af8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1fc067f401ec55e8a96a7905ad0862a9f4ffbbd6a948acaa8efcfd3e7ad0862(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__797456c5642d1112419068346020a1a633ab9aa84e7ed8ad9a057b833c92f5c3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    eks_access_key_id: typing.Optional[builtins.str] = None,
    eks_assume_role: typing.Optional[builtins.str] = None,
    eks_cluster_ca_cert: typing.Optional[builtins.str] = None,
    eks_cluster_endpoint: typing.Optional[builtins.str] = None,
    eks_cluster_name: typing.Optional[builtins.str] = None,
    eks_region: typing.Optional[builtins.str] = None,
    eks_secret_access_key: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
