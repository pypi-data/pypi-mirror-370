'''
# `akeyless_dynamic_secret_eks`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_eks`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks).
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


class DynamicSecretEks(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretEks.DynamicSecretEks",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks akeyless_dynamic_secret_eks}.'''

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
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks akeyless_dynamic_secret_eks} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#name DynamicSecretEks#name}
        :param eks_access_key_id: EKS Access Key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_access_key_id DynamicSecretEks#eks_access_key_id}
        :param eks_assume_role: Role ARN. Role to assume when connecting to the EKS cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_assume_role DynamicSecretEks#eks_assume_role}
        :param eks_cluster_ca_cert: EKS Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_ca_cert DynamicSecretEks#eks_cluster_ca_cert}
        :param eks_cluster_endpoint: EKS Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_endpoint DynamicSecretEks#eks_cluster_endpoint}
        :param eks_cluster_name: EKS cluster name. Must match the EKS cluster name you want to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_name DynamicSecretEks#eks_cluster_name}
        :param eks_region: EKS Region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_region DynamicSecretEks#eks_region}
        :param eks_secret_access_key: EKS Secret Access Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_secret_access_key DynamicSecretEks#eks_secret_access_key}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#encryption_key_name DynamicSecretEks#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#id DynamicSecretEks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_allow_port_forwading DynamicSecretEks#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_bastion_issuer DynamicSecretEks#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_cluster_endpoint DynamicSecretEks#secure_access_cluster_endpoint}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_enable DynamicSecretEks#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_web DynamicSecretEks#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#tags DynamicSecretEks#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#target_name DynamicSecretEks#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#user_ttl DynamicSecretEks#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59066da66aa50837d6ff49d3b70874898c9af7c808eb39a996085d5e75e917e8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretEksConfig(
            name=name,
            eks_access_key_id=eks_access_key_id,
            eks_assume_role=eks_assume_role,
            eks_cluster_ca_cert=eks_cluster_ca_cert,
            eks_cluster_endpoint=eks_cluster_endpoint,
            eks_cluster_name=eks_cluster_name,
            eks_region=eks_region,
            eks_secret_access_key=eks_secret_access_key,
            encryption_key_name=encryption_key_name,
            id=id,
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
        '''Generates CDKTF code for importing a DynamicSecretEks resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretEks to import.
        :param import_from_id: The id of the existing DynamicSecretEks that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretEks to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__659f36464ce86c071ce6587b5b3c33954ddd89be385d509a7789f3b3eb1e2d30)
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

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
            type_hints = typing.get_type_hints(_typecheckingstub__94cb57ddf22186df277ae3af3ee1e96e49c4e7814c33d11051d9e3f2155ca560)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksAccessKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="eksAssumeRole")
    def eks_assume_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksAssumeRole"))

    @eks_assume_role.setter
    def eks_assume_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55504e496dbf1b8c479d76dede5015867dc826f0ac2ae0f291b2980566210cbe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksAssumeRole", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterCaCert")
    def eks_cluster_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterCaCert"))

    @eks_cluster_ca_cert.setter
    def eks_cluster_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbf733301e7d40805a4da08825d23bae67f1b4fca1edb1574e3c09a42890c7c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterCaCert", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterEndpoint")
    def eks_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterEndpoint"))

    @eks_cluster_endpoint.setter
    def eks_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b5d7f640fcb99475c240e67297bcc65e4f303b8d005fa1abf79106b5302f94a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterName")
    def eks_cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterName"))

    @eks_cluster_name.setter
    def eks_cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48c7a9b4896b3bc755a461035bef47c9439f3d72250bf67346faf41f629521cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterName", value)

    @builtins.property
    @jsii.member(jsii_name="eksRegion")
    def eks_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksRegion"))

    @eks_region.setter
    def eks_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d717c85590128c567fe2eb855dfa4902ff5ff486dc6c7e1de479c90c5506649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksRegion", value)

    @builtins.property
    @jsii.member(jsii_name="eksSecretAccessKey")
    def eks_secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksSecretAccessKey"))

    @eks_secret_access_key.setter
    def eks_secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed9a840e1c4fb6160a4d104006113bcc311057d0e7e5a0a87b39ea2b9790898f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksSecretAccessKey", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__988b69c4f7fb0df08f9782377b11052a02bc769abf9d507a640198a3151a59b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d18832642ab60013267d331496b0681f68a988b929a8a470864a7520d2c4ec1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cefcdc95f8d0cc1badf58cd9526754e4b505c996ac7f824d33bc2353e291afdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__5c5b5bab3d0783dc1777567e91d9e37e510205cc12821ad82d30d110c2f0e406)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAllowPortForwading", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0bd95c9d1827bca581a52cfa8714332a75472912a352a8caa87421acd648b74a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessClusterEndpoint")
    def secure_access_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessClusterEndpoint"))

    @secure_access_cluster_endpoint.setter
    def secure_access_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5afa9da9f7025bb2ccbd8563ac3d513f9c172163fa68c3a2a2eaa29a6ea73f98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93e561559bba34d4b24b0a340d67dc5cc79b286c375f4374e92a111c5620e51b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__27f995b8f16aa0735e1d1fc3a66af57de83e3ce56f4a23e1ce1821fc31818ade)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__951c1a02595bb578d91f821f528c391b38d7bf09f2fdc3447120bf9e28137b77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__319ec3f9b30ac5d1d09ece9454557dfee5d84bd3200b11eb3043cf7b58aedf8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2bb60587546aa15fa28e6e7ae0fc78756fdbce9903a9ba1e4334ee2c65ed4f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretEks.DynamicSecretEksConfig",
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
        "encryption_key_name": "encryptionKeyName",
        "id": "id",
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
class DynamicSecretEksConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#name DynamicSecretEks#name}
        :param eks_access_key_id: EKS Access Key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_access_key_id DynamicSecretEks#eks_access_key_id}
        :param eks_assume_role: Role ARN. Role to assume when connecting to the EKS cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_assume_role DynamicSecretEks#eks_assume_role}
        :param eks_cluster_ca_cert: EKS Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_ca_cert DynamicSecretEks#eks_cluster_ca_cert}
        :param eks_cluster_endpoint: EKS Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_endpoint DynamicSecretEks#eks_cluster_endpoint}
        :param eks_cluster_name: EKS cluster name. Must match the EKS cluster name you want to connect to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_name DynamicSecretEks#eks_cluster_name}
        :param eks_region: EKS Region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_region DynamicSecretEks#eks_region}
        :param eks_secret_access_key: EKS Secret Access Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_secret_access_key DynamicSecretEks#eks_secret_access_key}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#encryption_key_name DynamicSecretEks#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#id DynamicSecretEks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_allow_port_forwading DynamicSecretEks#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_bastion_issuer DynamicSecretEks#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_cluster_endpoint DynamicSecretEks#secure_access_cluster_endpoint}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_enable DynamicSecretEks#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_web DynamicSecretEks#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#tags DynamicSecretEks#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#target_name DynamicSecretEks#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#user_ttl DynamicSecretEks#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db34e27d019449401b01f35e06b072805d0d7a91db608992d5eb0b040788e65e)
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
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
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
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if id is not None:
            self._values["id"] = id
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
        '''Dynamic secret name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#name DynamicSecretEks#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eks_access_key_id(self) -> typing.Optional[builtins.str]:
        '''EKS Access Key ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_access_key_id DynamicSecretEks#eks_access_key_id}
        '''
        result = self._values.get("eks_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_assume_role(self) -> typing.Optional[builtins.str]:
        '''Role ARN. Role to assume when connecting to the EKS cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_assume_role DynamicSecretEks#eks_assume_role}
        '''
        result = self._values.get("eks_assume_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_cluster_ca_cert(self) -> typing.Optional[builtins.str]:
        '''EKS Cluster certificate. Base 64 encoded certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_ca_cert DynamicSecretEks#eks_cluster_ca_cert}
        '''
        result = self._values.get("eks_cluster_ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''EKS Cluster endpoint. https:// , <DNS / IP> of the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_endpoint DynamicSecretEks#eks_cluster_endpoint}
        '''
        result = self._values.get("eks_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_cluster_name(self) -> typing.Optional[builtins.str]:
        '''EKS cluster name. Must match the EKS cluster name you want to connect to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_cluster_name DynamicSecretEks#eks_cluster_name}
        '''
        result = self._values.get("eks_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_region(self) -> typing.Optional[builtins.str]:
        '''EKS Region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_region DynamicSecretEks#eks_region}
        '''
        result = self._values.get("eks_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_secret_access_key(self) -> typing.Optional[builtins.str]:
        '''EKS Secret Access Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#eks_secret_access_key DynamicSecretEks#eks_secret_access_key}
        '''
        result = self._values.get("eks_secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#encryption_key_name DynamicSecretEks#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#id DynamicSecretEks#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_allow_port_forwading(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Port forwarding while using CLI access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_allow_port_forwading DynamicSecretEks#secure_access_allow_port_forwading}
        '''
        result = self._values.get("secure_access_allow_port_forwading")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_bastion_issuer DynamicSecretEks#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''The K8s cluster endpoint URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_cluster_endpoint DynamicSecretEks#secure_access_cluster_endpoint}
        '''
        result = self._values.get("secure_access_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_enable DynamicSecretEks#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#secure_access_web DynamicSecretEks#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#tags DynamicSecretEks#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#target_name DynamicSecretEks#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_eks#user_ttl DynamicSecretEks#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretEksConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretEks",
    "DynamicSecretEksConfig",
]

publication.publish()

def _typecheckingstub__59066da66aa50837d6ff49d3b70874898c9af7c808eb39a996085d5e75e917e8(
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
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__659f36464ce86c071ce6587b5b3c33954ddd89be385d509a7789f3b3eb1e2d30(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94cb57ddf22186df277ae3af3ee1e96e49c4e7814c33d11051d9e3f2155ca560(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55504e496dbf1b8c479d76dede5015867dc826f0ac2ae0f291b2980566210cbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbf733301e7d40805a4da08825d23bae67f1b4fca1edb1574e3c09a42890c7c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b5d7f640fcb99475c240e67297bcc65e4f303b8d005fa1abf79106b5302f94a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48c7a9b4896b3bc755a461035bef47c9439f3d72250bf67346faf41f629521cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d717c85590128c567fe2eb855dfa4902ff5ff486dc6c7e1de479c90c5506649(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed9a840e1c4fb6160a4d104006113bcc311057d0e7e5a0a87b39ea2b9790898f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__988b69c4f7fb0df08f9782377b11052a02bc769abf9d507a640198a3151a59b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d18832642ab60013267d331496b0681f68a988b929a8a470864a7520d2c4ec1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cefcdc95f8d0cc1badf58cd9526754e4b505c996ac7f824d33bc2353e291afdc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c5b5bab3d0783dc1777567e91d9e37e510205cc12821ad82d30d110c2f0e406(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0bd95c9d1827bca581a52cfa8714332a75472912a352a8caa87421acd648b74a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5afa9da9f7025bb2ccbd8563ac3d513f9c172163fa68c3a2a2eaa29a6ea73f98(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93e561559bba34d4b24b0a340d67dc5cc79b286c375f4374e92a111c5620e51b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27f995b8f16aa0735e1d1fc3a66af57de83e3ce56f4a23e1ce1821fc31818ade(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__951c1a02595bb578d91f821f528c391b38d7bf09f2fdc3447120bf9e28137b77(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__319ec3f9b30ac5d1d09ece9454557dfee5d84bd3200b11eb3043cf7b58aedf8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2bb60587546aa15fa28e6e7ae0fc78756fdbce9903a9ba1e4334ee2c65ed4f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db34e27d019449401b01f35e06b072805d0d7a91db608992d5eb0b040788e65e(
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
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
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
