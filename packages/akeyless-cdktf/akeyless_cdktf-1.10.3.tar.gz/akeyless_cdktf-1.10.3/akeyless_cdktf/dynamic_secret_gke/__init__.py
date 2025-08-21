'''
# `akeyless_dynamic_secret_gke`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_gke`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke).
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


class DynamicSecretGke(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretGke.DynamicSecretGke",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke akeyless_dynamic_secret_gke}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        encryption_key_name: typing.Optional[builtins.str] = None,
        gke_account_key: typing.Optional[builtins.str] = None,
        gke_cluster_cert: typing.Optional[builtins.str] = None,
        gke_cluster_endpoint: typing.Optional[builtins.str] = None,
        gke_cluster_name: typing.Optional[builtins.str] = None,
        gke_service_account_email: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke akeyless_dynamic_secret_gke} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#name DynamicSecretGke#name}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#encryption_key_name DynamicSecretGke#encryption_key_name}
        :param gke_account_key: GKE service account key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_account_key DynamicSecretGke#gke_account_key}
        :param gke_cluster_cert: GKE Base-64 encoded cluster certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_cert DynamicSecretGke#gke_cluster_cert}
        :param gke_cluster_endpoint: GKE cluster endpoint, i.e., cluster URI https://<DNS/IP>. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_endpoint DynamicSecretGke#gke_cluster_endpoint}
        :param gke_cluster_name: GKE cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_name DynamicSecretGke#gke_cluster_name}
        :param gke_service_account_email: GKE service account email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_service_account_email DynamicSecretGke#gke_service_account_email}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#id DynamicSecretGke#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_allow_port_forwading DynamicSecretGke#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_bastion_issuer DynamicSecretGke#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_cluster_endpoint DynamicSecretGke#secure_access_cluster_endpoint}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_enable DynamicSecretGke#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_web DynamicSecretGke#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#tags DynamicSecretGke#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#target_name DynamicSecretGke#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#user_ttl DynamicSecretGke#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8007840ef7d46e83b4df64ebf14996f89de886258d3a52b5bf54f65afa9d81e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretGkeConfig(
            name=name,
            encryption_key_name=encryption_key_name,
            gke_account_key=gke_account_key,
            gke_cluster_cert=gke_cluster_cert,
            gke_cluster_endpoint=gke_cluster_endpoint,
            gke_cluster_name=gke_cluster_name,
            gke_service_account_email=gke_service_account_email,
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
        '''Generates CDKTF code for importing a DynamicSecretGke resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretGke to import.
        :param import_from_id: The id of the existing DynamicSecretGke that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretGke to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c3dc1f2da28d337a2dd8928e33e41a9ecd319583ae79338cdbdedfdd0427e6a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

    @jsii.member(jsii_name="resetGkeAccountKey")
    def reset_gke_account_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeAccountKey", []))

    @jsii.member(jsii_name="resetGkeClusterCert")
    def reset_gke_cluster_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeClusterCert", []))

    @jsii.member(jsii_name="resetGkeClusterEndpoint")
    def reset_gke_cluster_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeClusterEndpoint", []))

    @jsii.member(jsii_name="resetGkeClusterName")
    def reset_gke_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeClusterName", []))

    @jsii.member(jsii_name="resetGkeServiceAccountEmail")
    def reset_gke_service_account_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGkeServiceAccountEmail", []))

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
    @jsii.member(jsii_name="encryptionKeyNameInput")
    def encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeAccountKeyInput")
    def gke_account_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gkeAccountKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterCertInput")
    def gke_cluster_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gkeClusterCertInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterEndpointInput")
    def gke_cluster_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gkeClusterEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeClusterNameInput")
    def gke_cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gkeClusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="gkeServiceAccountEmailInput")
    def gke_service_account_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gkeServiceAccountEmailInput"))

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
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57c9eb4b15332703dcea2ef8abbc681d6cd7969d8871d50407016c5906f122ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="gkeAccountKey")
    def gke_account_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeAccountKey"))

    @gke_account_key.setter
    def gke_account_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__083160b3e9e907c53ffad1857138a0803bbb809dbc32846f293a721f5cf5b04e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeAccountKey", value)

    @builtins.property
    @jsii.member(jsii_name="gkeClusterCert")
    def gke_cluster_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterCert"))

    @gke_cluster_cert.setter
    def gke_cluster_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3be718f1dbdf04a8a4291e2a4208dc4c6fabedf767614e8474bffe99280dd6c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterCert", value)

    @builtins.property
    @jsii.member(jsii_name="gkeClusterEndpoint")
    def gke_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterEndpoint"))

    @gke_cluster_endpoint.setter
    def gke_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bad2ed93908cbd4f81785303ce19627e598b77fa9f6dd577e7bd82feab62d83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="gkeClusterName")
    def gke_cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterName"))

    @gke_cluster_name.setter
    def gke_cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__395977fcd083dc68257a0904547df2566bd659a84b1c5ae2e01f630eee9f80e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterName", value)

    @builtins.property
    @jsii.member(jsii_name="gkeServiceAccountEmail")
    def gke_service_account_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeServiceAccountEmail"))

    @gke_service_account_email.setter
    def gke_service_account_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe3066e510a7e321645d4b10145eb1b64b9d838952f20b2cb6b397e636d370f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeServiceAccountEmail", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05e06f47d3184192783410d7785edfce9b1ed2213f5d483e3bcf25029c5fa771)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb0b03d66b066c4f82e23fb134086dca94167e62f784b260608c31cdcfec51e7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb1b3eef72f25623621f0895f2165e423887bb18f9c7c32cd12dc785101b275b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAllowPortForwading", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0cb7ad9d80081d12fdce2d1999b8802470bbdc6187dec220452e68122eb5227)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessClusterEndpoint")
    def secure_access_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessClusterEndpoint"))

    @secure_access_cluster_endpoint.setter
    def secure_access_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b5d92d855de0ef55aaad6da54416539ac2a4411791010c5bf17fca1a3e53148)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa29de3b3325f8146f092553ca8bd62837459027d1e998994aa2517fa503674)
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
            type_hints = typing.get_type_hints(_typecheckingstub__734f61b831a8ac5b79f7f27934ea5917cb0eadbb81d5b3b3f1e74cfc64c9a60f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5757d96db178cfb750d1c570b357d3309bd9d743b849020f5db8c94e2e4c5677)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a05564207b34a82aeceb918d8132ab9dfa23cdaf8e828b1d24881463abf096c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__214bd38e7c93c5a09165095f034d8c98e6b7c8acac1cf6687b1171e1b3fa4eb1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretGke.DynamicSecretGkeConfig",
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
        "encryption_key_name": "encryptionKeyName",
        "gke_account_key": "gkeAccountKey",
        "gke_cluster_cert": "gkeClusterCert",
        "gke_cluster_endpoint": "gkeClusterEndpoint",
        "gke_cluster_name": "gkeClusterName",
        "gke_service_account_email": "gkeServiceAccountEmail",
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
class DynamicSecretGkeConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        encryption_key_name: typing.Optional[builtins.str] = None,
        gke_account_key: typing.Optional[builtins.str] = None,
        gke_cluster_cert: typing.Optional[builtins.str] = None,
        gke_cluster_endpoint: typing.Optional[builtins.str] = None,
        gke_cluster_name: typing.Optional[builtins.str] = None,
        gke_service_account_email: typing.Optional[builtins.str] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#name DynamicSecretGke#name}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#encryption_key_name DynamicSecretGke#encryption_key_name}
        :param gke_account_key: GKE service account key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_account_key DynamicSecretGke#gke_account_key}
        :param gke_cluster_cert: GKE Base-64 encoded cluster certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_cert DynamicSecretGke#gke_cluster_cert}
        :param gke_cluster_endpoint: GKE cluster endpoint, i.e., cluster URI https://<DNS/IP>. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_endpoint DynamicSecretGke#gke_cluster_endpoint}
        :param gke_cluster_name: GKE cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_name DynamicSecretGke#gke_cluster_name}
        :param gke_service_account_email: GKE service account email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_service_account_email DynamicSecretGke#gke_service_account_email}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#id DynamicSecretGke#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_allow_port_forwading DynamicSecretGke#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_bastion_issuer DynamicSecretGke#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_cluster_endpoint DynamicSecretGke#secure_access_cluster_endpoint}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_enable DynamicSecretGke#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_web DynamicSecretGke#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#tags DynamicSecretGke#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#target_name DynamicSecretGke#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#user_ttl DynamicSecretGke#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__097e5153db9dc55321e36d9761c25b1be82bd5286d4adaef0b8c554fd2e5f694)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument gke_account_key", value=gke_account_key, expected_type=type_hints["gke_account_key"])
            check_type(argname="argument gke_cluster_cert", value=gke_cluster_cert, expected_type=type_hints["gke_cluster_cert"])
            check_type(argname="argument gke_cluster_endpoint", value=gke_cluster_endpoint, expected_type=type_hints["gke_cluster_endpoint"])
            check_type(argname="argument gke_cluster_name", value=gke_cluster_name, expected_type=type_hints["gke_cluster_name"])
            check_type(argname="argument gke_service_account_email", value=gke_service_account_email, expected_type=type_hints["gke_service_account_email"])
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
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if gke_account_key is not None:
            self._values["gke_account_key"] = gke_account_key
        if gke_cluster_cert is not None:
            self._values["gke_cluster_cert"] = gke_cluster_cert
        if gke_cluster_endpoint is not None:
            self._values["gke_cluster_endpoint"] = gke_cluster_endpoint
        if gke_cluster_name is not None:
            self._values["gke_cluster_name"] = gke_cluster_name
        if gke_service_account_email is not None:
            self._values["gke_service_account_email"] = gke_service_account_email
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#name DynamicSecretGke#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#encryption_key_name DynamicSecretGke#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_account_key(self) -> typing.Optional[builtins.str]:
        '''GKE service account key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_account_key DynamicSecretGke#gke_account_key}
        '''
        result = self._values.get("gke_account_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_cluster_cert(self) -> typing.Optional[builtins.str]:
        '''GKE Base-64 encoded cluster certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_cert DynamicSecretGke#gke_cluster_cert}
        '''
        result = self._values.get("gke_cluster_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''GKE cluster endpoint, i.e., cluster URI https://<DNS/IP>.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_endpoint DynamicSecretGke#gke_cluster_endpoint}
        '''
        result = self._values.get("gke_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_cluster_name(self) -> typing.Optional[builtins.str]:
        '''GKE cluster name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_cluster_name DynamicSecretGke#gke_cluster_name}
        '''
        result = self._values.get("gke_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_service_account_email(self) -> typing.Optional[builtins.str]:
        '''GKE service account email.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#gke_service_account_email DynamicSecretGke#gke_service_account_email}
        '''
        result = self._values.get("gke_service_account_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#id DynamicSecretGke#id}.

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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_allow_port_forwading DynamicSecretGke#secure_access_allow_port_forwading}
        '''
        result = self._values.get("secure_access_allow_port_forwading")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_bastion_issuer DynamicSecretGke#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''The K8s cluster endpoint URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_cluster_endpoint DynamicSecretGke#secure_access_cluster_endpoint}
        '''
        result = self._values.get("secure_access_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_enable DynamicSecretGke#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#secure_access_web DynamicSecretGke#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#tags DynamicSecretGke#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#target_name DynamicSecretGke#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_gke#user_ttl DynamicSecretGke#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretGkeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretGke",
    "DynamicSecretGkeConfig",
]

publication.publish()

def _typecheckingstub__8007840ef7d46e83b4df64ebf14996f89de886258d3a52b5bf54f65afa9d81e5(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    encryption_key_name: typing.Optional[builtins.str] = None,
    gke_account_key: typing.Optional[builtins.str] = None,
    gke_cluster_cert: typing.Optional[builtins.str] = None,
    gke_cluster_endpoint: typing.Optional[builtins.str] = None,
    gke_cluster_name: typing.Optional[builtins.str] = None,
    gke_service_account_email: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6c3dc1f2da28d337a2dd8928e33e41a9ecd319583ae79338cdbdedfdd0427e6a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c9eb4b15332703dcea2ef8abbc681d6cd7969d8871d50407016c5906f122ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__083160b3e9e907c53ffad1857138a0803bbb809dbc32846f293a721f5cf5b04e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3be718f1dbdf04a8a4291e2a4208dc4c6fabedf767614e8474bffe99280dd6c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bad2ed93908cbd4f81785303ce19627e598b77fa9f6dd577e7bd82feab62d83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__395977fcd083dc68257a0904547df2566bd659a84b1c5ae2e01f630eee9f80e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe3066e510a7e321645d4b10145eb1b64b9d838952f20b2cb6b397e636d370f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05e06f47d3184192783410d7785edfce9b1ed2213f5d483e3bcf25029c5fa771(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb0b03d66b066c4f82e23fb134086dca94167e62f784b260608c31cdcfec51e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb1b3eef72f25623621f0895f2165e423887bb18f9c7c32cd12dc785101b275b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0cb7ad9d80081d12fdce2d1999b8802470bbdc6187dec220452e68122eb5227(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b5d92d855de0ef55aaad6da54416539ac2a4411791010c5bf17fca1a3e53148(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fa29de3b3325f8146f092553ca8bd62837459027d1e998994aa2517fa503674(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__734f61b831a8ac5b79f7f27934ea5917cb0eadbb81d5b3b3f1e74cfc64c9a60f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5757d96db178cfb750d1c570b357d3309bd9d743b849020f5db8c94e2e4c5677(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a05564207b34a82aeceb918d8132ab9dfa23cdaf8e828b1d24881463abf096c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__214bd38e7c93c5a09165095f034d8c98e6b7c8acac1cf6687b1171e1b3fa4eb1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__097e5153db9dc55321e36d9761c25b1be82bd5286d4adaef0b8c554fd2e5f694(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    encryption_key_name: typing.Optional[builtins.str] = None,
    gke_account_key: typing.Optional[builtins.str] = None,
    gke_cluster_cert: typing.Optional[builtins.str] = None,
    gke_cluster_endpoint: typing.Optional[builtins.str] = None,
    gke_cluster_name: typing.Optional[builtins.str] = None,
    gke_service_account_email: typing.Optional[builtins.str] = None,
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
