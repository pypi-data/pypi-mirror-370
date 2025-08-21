'''
# `akeyless_producer_k8s`

Refer to the Terraform Registry for docs: [`akeyless_producer_k8s`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s).
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


class ProducerK8S(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerK8S.ProducerK8S",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s akeyless_producer_k8s}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        delete_protection: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        k8_s_allowed_namespaces: typing.Optional[builtins.str] = None,
        k8_s_cluster_ca_cert: typing.Optional[builtins.str] = None,
        k8_s_cluster_endpoint: typing.Optional[builtins.str] = None,
        k8_s_cluster_token: typing.Optional[builtins.str] = None,
        k8_s_namespace: typing.Optional[builtins.str] = None,
        k8_s_predefined_role_name: typing.Optional[builtins.str] = None,
        k8_s_predefined_role_type: typing.Optional[builtins.str] = None,
        k8_s_service_account: typing.Optional[builtins.str] = None,
        k8_s_service_account_type: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
        secure_access_dashboard_url: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_proxy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s akeyless_producer_k8s} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#name ProducerK8S#name}
        :param delete_protection: Protection from accidental deletion of this item [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#delete_protection ProducerK8S#delete_protection}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#id ProducerK8S#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param k8_s_allowed_namespaces: Comma-separated list of allowed K8S namespaces for the generated ServiceAccount (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_allowed_namespaces ProducerK8S#k8s_allowed_namespaces}
        :param k8_s_cluster_ca_cert: K8S Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_ca_cert ProducerK8S#k8s_cluster_ca_cert}
        :param k8_s_cluster_endpoint: K8S Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_endpoint ProducerK8S#k8s_cluster_endpoint}
        :param k8_s_cluster_token: K8S Cluster authentication token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_token ProducerK8S#k8s_cluster_token}
        :param k8_s_namespace: K8S Namespace where the ServiceAccount exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_namespace ProducerK8S#k8s_namespace}
        :param k8_s_predefined_role_name: The pre-existing Role or ClusterRole name to bind the generated ServiceAccount to (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_predefined_role_name ProducerK8S#k8s_predefined_role_name}
        :param k8_s_predefined_role_type: Specifies the type of the pre-existing K8S role [Role, ClusterRole] (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_predefined_role_type ProducerK8S#k8s_predefined_role_type}
        :param k8_s_service_account: K8S ServiceAccount to extract token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_service_account ProducerK8S#k8s_service_account}
        :param k8_s_service_account_type: K8S ServiceAccount type [fixed, dynamic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_service_account_type ProducerK8S#k8s_service_account_type}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#producer_encryption_key_name ProducerK8S#producer_encryption_key_name}
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_allow_port_forwading ProducerK8S#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_bastion_issuer ProducerK8S#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_cluster_endpoint ProducerK8S#secure_access_cluster_endpoint}
        :param secure_access_dashboard_url: The K8s dashboard url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_dashboard_url ProducerK8S#secure_access_dashboard_url}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_enable ProducerK8S#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web ProducerK8S#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web_browsing ProducerK8S#secure_access_web_browsing}
        :param secure_access_web_proxy: Web-Proxy via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web_proxy ProducerK8S#secure_access_web_proxy}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#tags ProducerK8S#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#target_name ProducerK8S#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#user_ttl ProducerK8S#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__145496e298667edfeccd97234b4b72df49efb74373f1e40df960a01df6c16e1c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerK8SConfig(
            name=name,
            delete_protection=delete_protection,
            id=id,
            k8_s_allowed_namespaces=k8_s_allowed_namespaces,
            k8_s_cluster_ca_cert=k8_s_cluster_ca_cert,
            k8_s_cluster_endpoint=k8_s_cluster_endpoint,
            k8_s_cluster_token=k8_s_cluster_token,
            k8_s_namespace=k8_s_namespace,
            k8_s_predefined_role_name=k8_s_predefined_role_name,
            k8_s_predefined_role_type=k8_s_predefined_role_type,
            k8_s_service_account=k8_s_service_account,
            k8_s_service_account_type=k8_s_service_account_type,
            producer_encryption_key_name=producer_encryption_key_name,
            secure_access_allow_port_forwading=secure_access_allow_port_forwading,
            secure_access_bastion_issuer=secure_access_bastion_issuer,
            secure_access_cluster_endpoint=secure_access_cluster_endpoint,
            secure_access_dashboard_url=secure_access_dashboard_url,
            secure_access_enable=secure_access_enable,
            secure_access_web=secure_access_web,
            secure_access_web_browsing=secure_access_web_browsing,
            secure_access_web_proxy=secure_access_web_proxy,
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
        '''Generates CDKTF code for importing a ProducerK8S resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerK8S to import.
        :param import_from_id: The id of the existing ProducerK8S that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerK8S to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f485bacb4bc4a859f22d47e4514494e38848e5d26442a2f0e23646f97146491a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetK8SAllowedNamespaces")
    def reset_k8_s_allowed_namespaces(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SAllowedNamespaces", []))

    @jsii.member(jsii_name="resetK8SClusterCaCert")
    def reset_k8_s_cluster_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SClusterCaCert", []))

    @jsii.member(jsii_name="resetK8SClusterEndpoint")
    def reset_k8_s_cluster_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SClusterEndpoint", []))

    @jsii.member(jsii_name="resetK8SClusterToken")
    def reset_k8_s_cluster_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SClusterToken", []))

    @jsii.member(jsii_name="resetK8SNamespace")
    def reset_k8_s_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SNamespace", []))

    @jsii.member(jsii_name="resetK8SPredefinedRoleName")
    def reset_k8_s_predefined_role_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SPredefinedRoleName", []))

    @jsii.member(jsii_name="resetK8SPredefinedRoleType")
    def reset_k8_s_predefined_role_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SPredefinedRoleType", []))

    @jsii.member(jsii_name="resetK8SServiceAccount")
    def reset_k8_s_service_account(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SServiceAccount", []))

    @jsii.member(jsii_name="resetK8SServiceAccountType")
    def reset_k8_s_service_account_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SServiceAccountType", []))

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

    @jsii.member(jsii_name="resetSecureAccessDashboardUrl")
    def reset_secure_access_dashboard_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessDashboardUrl", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

    @jsii.member(jsii_name="resetSecureAccessWeb")
    def reset_secure_access_web(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWeb", []))

    @jsii.member(jsii_name="resetSecureAccessWebBrowsing")
    def reset_secure_access_web_browsing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWebBrowsing", []))

    @jsii.member(jsii_name="resetSecureAccessWebProxy")
    def reset_secure_access_web_proxy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessWebProxy", []))

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
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SAllowedNamespacesInput")
    def k8_s_allowed_namespaces_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SAllowedNamespacesInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SClusterCaCertInput")
    def k8_s_cluster_ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SClusterCaCertInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SClusterEndpointInput")
    def k8_s_cluster_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SClusterEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SClusterTokenInput")
    def k8_s_cluster_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SClusterTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SNamespaceInput")
    def k8_s_namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SNamespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SPredefinedRoleNameInput")
    def k8_s_predefined_role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SPredefinedRoleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SPredefinedRoleTypeInput")
    def k8_s_predefined_role_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SPredefinedRoleTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SServiceAccountInput")
    def k8_s_service_account_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SServiceAccountInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SServiceAccountTypeInput")
    def k8_s_service_account_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SServiceAccountTypeInput"))

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
    @jsii.member(jsii_name="secureAccessDashboardUrlInput")
    def secure_access_dashboard_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessDashboardUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

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
    @jsii.member(jsii_name="secureAccessWebProxyInput")
    def secure_access_web_proxy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "secureAccessWebProxyInput"))

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
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbfc50d85441bb572dea23450d33d2bdc27d9509b7df445273857d487f7b41af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b94556bfa695372b92049c109b504efe39025235245d0c6aa23e713e8ea86a7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="k8SAllowedNamespaces")
    def k8_s_allowed_namespaces(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SAllowedNamespaces"))

    @k8_s_allowed_namespaces.setter
    def k8_s_allowed_namespaces(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85656f6ae07c3bc3aecfa72824c429a58c195ca7a25e29273576e7af0ce1e9c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SAllowedNamespaces", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClusterCaCert")
    def k8_s_cluster_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClusterCaCert"))

    @k8_s_cluster_ca_cert.setter
    def k8_s_cluster_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c16b0ee4a00272670ea3b9937a2bbc8446cc3bfefc005531e5c489fe6ce097b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClusterCaCert", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClusterEndpoint")
    def k8_s_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClusterEndpoint"))

    @k8_s_cluster_endpoint.setter
    def k8_s_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff5510fd97e769098ef3a0804933b438da820abb67e0150a5c3e9ab2beb525b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClusterToken")
    def k8_s_cluster_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClusterToken"))

    @k8_s_cluster_token.setter
    def k8_s_cluster_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20e98e88885ebf7a757cad15bd2d7cd23534e1bd51f8096bc6eeb7dfbe5eed03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClusterToken", value)

    @builtins.property
    @jsii.member(jsii_name="k8SNamespace")
    def k8_s_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SNamespace"))

    @k8_s_namespace.setter
    def k8_s_namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a434498a46697980d7cad962fe2b0f7e71691394c2caa3d0357c85be63263012)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SNamespace", value)

    @builtins.property
    @jsii.member(jsii_name="k8SPredefinedRoleName")
    def k8_s_predefined_role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SPredefinedRoleName"))

    @k8_s_predefined_role_name.setter
    def k8_s_predefined_role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baf586ec75a27130f3e1c0cda5f96555b4ddca24d7710601059cdbbb0f2dee0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SPredefinedRoleName", value)

    @builtins.property
    @jsii.member(jsii_name="k8SPredefinedRoleType")
    def k8_s_predefined_role_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SPredefinedRoleType"))

    @k8_s_predefined_role_type.setter
    def k8_s_predefined_role_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a35f9efe755f690b4901c249c689099a85e7fb6fc55d485b76a952238cbd07e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SPredefinedRoleType", value)

    @builtins.property
    @jsii.member(jsii_name="k8SServiceAccount")
    def k8_s_service_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SServiceAccount"))

    @k8_s_service_account.setter
    def k8_s_service_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a4621299314a07bcf7ad779fc5e9a0e425efa519576758e0f5dbf8e78f341ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SServiceAccount", value)

    @builtins.property
    @jsii.member(jsii_name="k8SServiceAccountType")
    def k8_s_service_account_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SServiceAccountType"))

    @k8_s_service_account_type.setter
    def k8_s_service_account_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d00213c9b2197cf43f3a992efe2bd9947e91163b3caf612d7c2ebe46d6dbdb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SServiceAccountType", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65531e9436390d526f74bf528ccf26dca98f493462eddb8a778752803b94e0a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84e69fdfe294d11f99df73522b6c5de38e81bd41e9c6613ed342eded2ae3c326)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3bba3a7fc58aabe8ad5ac09af1f3449931165f2fa61acc33faa8d51ad1a08f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAllowPortForwading", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b34976d5e0360593a4f0541bb32e3950e323799db24387a764d69bb4b91b0e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessClusterEndpoint")
    def secure_access_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessClusterEndpoint"))

    @secure_access_cluster_endpoint.setter
    def secure_access_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__804d71bcc4de86c296ea2c1896d6ff48533c9b906e08b14202c28e2a63e22c19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDashboardUrl")
    def secure_access_dashboard_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDashboardUrl"))

    @secure_access_dashboard_url.setter
    def secure_access_dashboard_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72188a9f97a1806d9f0210af7951a4c275618a0a936436541e4d796b34472c21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDashboardUrl", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53f441ab87d740cb840d5ce2faa0e7dce9dddd3db9500a1048c6d11005c987ce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca9609839119f0497f89048827d139b9b55c8944f7eef41d8f6fe53779f2db13)
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
            type_hints = typing.get_type_hints(_typecheckingstub__28a3466aa1f628a73a2970002258a158895f25627e8910aff85f507295bd278a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWebBrowsing", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessWebProxy")
    def secure_access_web_proxy(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "secureAccessWebProxy"))

    @secure_access_web_proxy.setter
    def secure_access_web_proxy(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a80f630a8f51beb94197345c87d58535b141993dbc9682889a038f45b9fe3900)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWebProxy", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6df687a0ccffd032dc86653afb8ed4858ca8a7471c3bdb7726457df2d2f6fad3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eca52df9e648bc5fd4931ae89850063bf1bdf26656a26738e8779da2318a8266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a79986bada5e469635922bdd8179907985c2c6f7568934e2152bd755236e96b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerK8S.ProducerK8SConfig",
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
        "delete_protection": "deleteProtection",
        "id": "id",
        "k8_s_allowed_namespaces": "k8SAllowedNamespaces",
        "k8_s_cluster_ca_cert": "k8SClusterCaCert",
        "k8_s_cluster_endpoint": "k8SClusterEndpoint",
        "k8_s_cluster_token": "k8SClusterToken",
        "k8_s_namespace": "k8SNamespace",
        "k8_s_predefined_role_name": "k8SPredefinedRoleName",
        "k8_s_predefined_role_type": "k8SPredefinedRoleType",
        "k8_s_service_account": "k8SServiceAccount",
        "k8_s_service_account_type": "k8SServiceAccountType",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "secure_access_allow_port_forwading": "secureAccessAllowPortForwading",
        "secure_access_bastion_issuer": "secureAccessBastionIssuer",
        "secure_access_cluster_endpoint": "secureAccessClusterEndpoint",
        "secure_access_dashboard_url": "secureAccessDashboardUrl",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_web": "secureAccessWeb",
        "secure_access_web_browsing": "secureAccessWebBrowsing",
        "secure_access_web_proxy": "secureAccessWebProxy",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerK8SConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        delete_protection: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        k8_s_allowed_namespaces: typing.Optional[builtins.str] = None,
        k8_s_cluster_ca_cert: typing.Optional[builtins.str] = None,
        k8_s_cluster_endpoint: typing.Optional[builtins.str] = None,
        k8_s_cluster_token: typing.Optional[builtins.str] = None,
        k8_s_namespace: typing.Optional[builtins.str] = None,
        k8_s_predefined_role_name: typing.Optional[builtins.str] = None,
        k8_s_predefined_role_type: typing.Optional[builtins.str] = None,
        k8_s_service_account: typing.Optional[builtins.str] = None,
        k8_s_service_account_type: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
        secure_access_dashboard_url: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        secure_access_web_proxy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#name ProducerK8S#name}
        :param delete_protection: Protection from accidental deletion of this item [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#delete_protection ProducerK8S#delete_protection}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#id ProducerK8S#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param k8_s_allowed_namespaces: Comma-separated list of allowed K8S namespaces for the generated ServiceAccount (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_allowed_namespaces ProducerK8S#k8s_allowed_namespaces}
        :param k8_s_cluster_ca_cert: K8S Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_ca_cert ProducerK8S#k8s_cluster_ca_cert}
        :param k8_s_cluster_endpoint: K8S Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_endpoint ProducerK8S#k8s_cluster_endpoint}
        :param k8_s_cluster_token: K8S Cluster authentication token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_token ProducerK8S#k8s_cluster_token}
        :param k8_s_namespace: K8S Namespace where the ServiceAccount exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_namespace ProducerK8S#k8s_namespace}
        :param k8_s_predefined_role_name: The pre-existing Role or ClusterRole name to bind the generated ServiceAccount to (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_predefined_role_name ProducerK8S#k8s_predefined_role_name}
        :param k8_s_predefined_role_type: Specifies the type of the pre-existing K8S role [Role, ClusterRole] (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_predefined_role_type ProducerK8S#k8s_predefined_role_type}
        :param k8_s_service_account: K8S ServiceAccount to extract token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_service_account ProducerK8S#k8s_service_account}
        :param k8_s_service_account_type: K8S ServiceAccount type [fixed, dynamic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_service_account_type ProducerK8S#k8s_service_account_type}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#producer_encryption_key_name ProducerK8S#producer_encryption_key_name}
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_allow_port_forwading ProducerK8S#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_bastion_issuer ProducerK8S#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_cluster_endpoint ProducerK8S#secure_access_cluster_endpoint}
        :param secure_access_dashboard_url: The K8s dashboard url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_dashboard_url ProducerK8S#secure_access_dashboard_url}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_enable ProducerK8S#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web ProducerK8S#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web_browsing ProducerK8S#secure_access_web_browsing}
        :param secure_access_web_proxy: Web-Proxy via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web_proxy ProducerK8S#secure_access_web_proxy}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#tags ProducerK8S#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#target_name ProducerK8S#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#user_ttl ProducerK8S#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba101418ec41788a9e7229a72fef88372fa0d301ae4e91b7fef4fe1d7c322f86)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument k8_s_allowed_namespaces", value=k8_s_allowed_namespaces, expected_type=type_hints["k8_s_allowed_namespaces"])
            check_type(argname="argument k8_s_cluster_ca_cert", value=k8_s_cluster_ca_cert, expected_type=type_hints["k8_s_cluster_ca_cert"])
            check_type(argname="argument k8_s_cluster_endpoint", value=k8_s_cluster_endpoint, expected_type=type_hints["k8_s_cluster_endpoint"])
            check_type(argname="argument k8_s_cluster_token", value=k8_s_cluster_token, expected_type=type_hints["k8_s_cluster_token"])
            check_type(argname="argument k8_s_namespace", value=k8_s_namespace, expected_type=type_hints["k8_s_namespace"])
            check_type(argname="argument k8_s_predefined_role_name", value=k8_s_predefined_role_name, expected_type=type_hints["k8_s_predefined_role_name"])
            check_type(argname="argument k8_s_predefined_role_type", value=k8_s_predefined_role_type, expected_type=type_hints["k8_s_predefined_role_type"])
            check_type(argname="argument k8_s_service_account", value=k8_s_service_account, expected_type=type_hints["k8_s_service_account"])
            check_type(argname="argument k8_s_service_account_type", value=k8_s_service_account_type, expected_type=type_hints["k8_s_service_account_type"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
            check_type(argname="argument secure_access_allow_port_forwading", value=secure_access_allow_port_forwading, expected_type=type_hints["secure_access_allow_port_forwading"])
            check_type(argname="argument secure_access_bastion_issuer", value=secure_access_bastion_issuer, expected_type=type_hints["secure_access_bastion_issuer"])
            check_type(argname="argument secure_access_cluster_endpoint", value=secure_access_cluster_endpoint, expected_type=type_hints["secure_access_cluster_endpoint"])
            check_type(argname="argument secure_access_dashboard_url", value=secure_access_dashboard_url, expected_type=type_hints["secure_access_dashboard_url"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_web", value=secure_access_web, expected_type=type_hints["secure_access_web"])
            check_type(argname="argument secure_access_web_browsing", value=secure_access_web_browsing, expected_type=type_hints["secure_access_web_browsing"])
            check_type(argname="argument secure_access_web_proxy", value=secure_access_web_proxy, expected_type=type_hints["secure_access_web_proxy"])
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
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if id is not None:
            self._values["id"] = id
        if k8_s_allowed_namespaces is not None:
            self._values["k8_s_allowed_namespaces"] = k8_s_allowed_namespaces
        if k8_s_cluster_ca_cert is not None:
            self._values["k8_s_cluster_ca_cert"] = k8_s_cluster_ca_cert
        if k8_s_cluster_endpoint is not None:
            self._values["k8_s_cluster_endpoint"] = k8_s_cluster_endpoint
        if k8_s_cluster_token is not None:
            self._values["k8_s_cluster_token"] = k8_s_cluster_token
        if k8_s_namespace is not None:
            self._values["k8_s_namespace"] = k8_s_namespace
        if k8_s_predefined_role_name is not None:
            self._values["k8_s_predefined_role_name"] = k8_s_predefined_role_name
        if k8_s_predefined_role_type is not None:
            self._values["k8_s_predefined_role_type"] = k8_s_predefined_role_type
        if k8_s_service_account is not None:
            self._values["k8_s_service_account"] = k8_s_service_account
        if k8_s_service_account_type is not None:
            self._values["k8_s_service_account_type"] = k8_s_service_account_type
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
        if secure_access_allow_port_forwading is not None:
            self._values["secure_access_allow_port_forwading"] = secure_access_allow_port_forwading
        if secure_access_bastion_issuer is not None:
            self._values["secure_access_bastion_issuer"] = secure_access_bastion_issuer
        if secure_access_cluster_endpoint is not None:
            self._values["secure_access_cluster_endpoint"] = secure_access_cluster_endpoint
        if secure_access_dashboard_url is not None:
            self._values["secure_access_dashboard_url"] = secure_access_dashboard_url
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_web is not None:
            self._values["secure_access_web"] = secure_access_web
        if secure_access_web_browsing is not None:
            self._values["secure_access_web_browsing"] = secure_access_web_browsing
        if secure_access_web_proxy is not None:
            self._values["secure_access_web_proxy"] = secure_access_web_proxy
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#name ProducerK8S#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this item [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#delete_protection ProducerK8S#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#id ProducerK8S#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_allowed_namespaces(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of allowed K8S namespaces for the generated ServiceAccount (relevant only for k8s-service-account-type=dynamic).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_allowed_namespaces ProducerK8S#k8s_allowed_namespaces}
        '''
        result = self._values.get("k8_s_allowed_namespaces")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_cluster_ca_cert(self) -> typing.Optional[builtins.str]:
        '''K8S Cluster certificate. Base 64 encoded certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_ca_cert ProducerK8S#k8s_cluster_ca_cert}
        '''
        result = self._values.get("k8_s_cluster_ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''K8S Cluster endpoint. https:// , <DNS / IP> of the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_endpoint ProducerK8S#k8s_cluster_endpoint}
        '''
        result = self._values.get("k8_s_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_cluster_token(self) -> typing.Optional[builtins.str]:
        '''K8S Cluster authentication token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_cluster_token ProducerK8S#k8s_cluster_token}
        '''
        result = self._values.get("k8_s_cluster_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_namespace(self) -> typing.Optional[builtins.str]:
        '''K8S Namespace where the ServiceAccount exists.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_namespace ProducerK8S#k8s_namespace}
        '''
        result = self._values.get("k8_s_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_predefined_role_name(self) -> typing.Optional[builtins.str]:
        '''The pre-existing Role or ClusterRole name to bind the generated ServiceAccount to (relevant only for k8s-service-account-type=dynamic).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_predefined_role_name ProducerK8S#k8s_predefined_role_name}
        '''
        result = self._values.get("k8_s_predefined_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_predefined_role_type(self) -> typing.Optional[builtins.str]:
        '''Specifies the type of the pre-existing K8S role [Role, ClusterRole] (relevant only for k8s-service-account-type=dynamic).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_predefined_role_type ProducerK8S#k8s_predefined_role_type}
        '''
        result = self._values.get("k8_s_predefined_role_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_service_account(self) -> typing.Optional[builtins.str]:
        '''K8S ServiceAccount to extract token from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_service_account ProducerK8S#k8s_service_account}
        '''
        result = self._values.get("k8_s_service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_service_account_type(self) -> typing.Optional[builtins.str]:
        '''K8S ServiceAccount type [fixed, dynamic].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#k8s_service_account_type ProducerK8S#k8s_service_account_type}
        '''
        result = self._values.get("k8_s_service_account_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#producer_encryption_key_name ProducerK8S#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_allow_port_forwading(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Port forwarding while using CLI access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_allow_port_forwading ProducerK8S#secure_access_allow_port_forwading}
        '''
        result = self._values.get("secure_access_allow_port_forwading")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_bastion_issuer ProducerK8S#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''The K8s cluster endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_cluster_endpoint ProducerK8S#secure_access_cluster_endpoint}
        '''
        result = self._values.get("secure_access_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_dashboard_url(self) -> typing.Optional[builtins.str]:
        '''The K8s dashboard url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_dashboard_url ProducerK8S#secure_access_dashboard_url}
        '''
        result = self._values.get("secure_access_dashboard_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_enable ProducerK8S#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web ProducerK8S#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_web_browsing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Secure browser via Akeyless Web Access Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web_browsing ProducerK8S#secure_access_web_browsing}
        '''
        result = self._values.get("secure_access_web_browsing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_web_proxy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Web-Proxy via Akeyless Web Access Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#secure_access_web_proxy ProducerK8S#secure_access_web_proxy}
        '''
        result = self._values.get("secure_access_web_proxy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#tags ProducerK8S#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#target_name ProducerK8S#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_k8s#user_ttl ProducerK8S#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerK8SConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerK8S",
    "ProducerK8SConfig",
]

publication.publish()

def _typecheckingstub__145496e298667edfeccd97234b4b72df49efb74373f1e40df960a01df6c16e1c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    delete_protection: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    k8_s_allowed_namespaces: typing.Optional[builtins.str] = None,
    k8_s_cluster_ca_cert: typing.Optional[builtins.str] = None,
    k8_s_cluster_endpoint: typing.Optional[builtins.str] = None,
    k8_s_cluster_token: typing.Optional[builtins.str] = None,
    k8_s_namespace: typing.Optional[builtins.str] = None,
    k8_s_predefined_role_name: typing.Optional[builtins.str] = None,
    k8_s_predefined_role_type: typing.Optional[builtins.str] = None,
    k8_s_service_account: typing.Optional[builtins.str] = None,
    k8_s_service_account_type: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
    secure_access_dashboard_url: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_proxy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__f485bacb4bc4a859f22d47e4514494e38848e5d26442a2f0e23646f97146491a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbfc50d85441bb572dea23450d33d2bdc27d9509b7df445273857d487f7b41af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b94556bfa695372b92049c109b504efe39025235245d0c6aa23e713e8ea86a7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85656f6ae07c3bc3aecfa72824c429a58c195ca7a25e29273576e7af0ce1e9c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c16b0ee4a00272670ea3b9937a2bbc8446cc3bfefc005531e5c489fe6ce097b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff5510fd97e769098ef3a0804933b438da820abb67e0150a5c3e9ab2beb525b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20e98e88885ebf7a757cad15bd2d7cd23534e1bd51f8096bc6eeb7dfbe5eed03(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a434498a46697980d7cad962fe2b0f7e71691394c2caa3d0357c85be63263012(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baf586ec75a27130f3e1c0cda5f96555b4ddca24d7710601059cdbbb0f2dee0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a35f9efe755f690b4901c249c689099a85e7fb6fc55d485b76a952238cbd07e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a4621299314a07bcf7ad779fc5e9a0e425efa519576758e0f5dbf8e78f341ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d00213c9b2197cf43f3a992efe2bd9947e91163b3caf612d7c2ebe46d6dbdb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65531e9436390d526f74bf528ccf26dca98f493462eddb8a778752803b94e0a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84e69fdfe294d11f99df73522b6c5de38e81bd41e9c6613ed342eded2ae3c326(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3bba3a7fc58aabe8ad5ac09af1f3449931165f2fa61acc33faa8d51ad1a08f5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b34976d5e0360593a4f0541bb32e3950e323799db24387a764d69bb4b91b0e6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__804d71bcc4de86c296ea2c1896d6ff48533c9b906e08b14202c28e2a63e22c19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72188a9f97a1806d9f0210af7951a4c275618a0a936436541e4d796b34472c21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53f441ab87d740cb840d5ce2faa0e7dce9dddd3db9500a1048c6d11005c987ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca9609839119f0497f89048827d139b9b55c8944f7eef41d8f6fe53779f2db13(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28a3466aa1f628a73a2970002258a158895f25627e8910aff85f507295bd278a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a80f630a8f51beb94197345c87d58535b141993dbc9682889a038f45b9fe3900(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6df687a0ccffd032dc86653afb8ed4858ca8a7471c3bdb7726457df2d2f6fad3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eca52df9e648bc5fd4931ae89850063bf1bdf26656a26738e8779da2318a8266(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a79986bada5e469635922bdd8179907985c2c6f7568934e2152bd755236e96b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba101418ec41788a9e7229a72fef88372fa0d301ae4e91b7fef4fe1d7c322f86(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    delete_protection: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    k8_s_allowed_namespaces: typing.Optional[builtins.str] = None,
    k8_s_cluster_ca_cert: typing.Optional[builtins.str] = None,
    k8_s_cluster_endpoint: typing.Optional[builtins.str] = None,
    k8_s_cluster_token: typing.Optional[builtins.str] = None,
    k8_s_namespace: typing.Optional[builtins.str] = None,
    k8_s_predefined_role_name: typing.Optional[builtins.str] = None,
    k8_s_predefined_role_type: typing.Optional[builtins.str] = None,
    k8_s_service_account: typing.Optional[builtins.str] = None,
    k8_s_service_account_type: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    secure_access_allow_port_forwading: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_cluster_endpoint: typing.Optional[builtins.str] = None,
    secure_access_dashboard_url: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_browsing: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    secure_access_web_proxy: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
