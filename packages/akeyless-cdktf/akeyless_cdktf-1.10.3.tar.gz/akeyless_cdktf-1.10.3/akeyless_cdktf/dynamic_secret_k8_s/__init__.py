'''
# `akeyless_dynamic_secret_k8s`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_k8s`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s).
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


class DynamicSecretK8S(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretK8S.DynamicSecretK8S",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s akeyless_dynamic_secret_k8s}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        custom_username_template: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s akeyless_dynamic_secret_k8s} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#name DynamicSecretK8S#name}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#custom_username_template DynamicSecretK8S#custom_username_template}
        :param delete_protection: Protection from accidental deletion of this item [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#delete_protection DynamicSecretK8S#delete_protection}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#encryption_key_name DynamicSecretK8S#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#id DynamicSecretK8S#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param k8_s_allowed_namespaces: Comma-separated list of allowed K8S namespaces for the generated ServiceAccount (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_allowed_namespaces DynamicSecretK8S#k8s_allowed_namespaces}
        :param k8_s_cluster_ca_cert: K8S Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_ca_cert DynamicSecretK8S#k8s_cluster_ca_cert}
        :param k8_s_cluster_endpoint: K8S Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_endpoint DynamicSecretK8S#k8s_cluster_endpoint}
        :param k8_s_cluster_token: K8S Cluster authentication token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_token DynamicSecretK8S#k8s_cluster_token}
        :param k8_s_namespace: K8S Namespace where the ServiceAccount exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_namespace DynamicSecretK8S#k8s_namespace}
        :param k8_s_predefined_role_name: The pre-existing Role or ClusterRole name to bind the generated ServiceAccount to (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_predefined_role_name DynamicSecretK8S#k8s_predefined_role_name}
        :param k8_s_predefined_role_type: Specifies the type of the pre-existing K8S role [Role, ClusterRole] (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_predefined_role_type DynamicSecretK8S#k8s_predefined_role_type}
        :param k8_s_service_account: K8S ServiceAccount to extract token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_service_account DynamicSecretK8S#k8s_service_account}
        :param k8_s_service_account_type: K8S ServiceAccount type [fixed, dynamic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_service_account_type DynamicSecretK8S#k8s_service_account_type}
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_allow_port_forwading DynamicSecretK8S#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_bastion_issuer DynamicSecretK8S#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_cluster_endpoint DynamicSecretK8S#secure_access_cluster_endpoint}
        :param secure_access_dashboard_url: The K8s dashboard url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_dashboard_url DynamicSecretK8S#secure_access_dashboard_url}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_enable DynamicSecretK8S#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web DynamicSecretK8S#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web_browsing DynamicSecretK8S#secure_access_web_browsing}
        :param secure_access_web_proxy: Web-Proxy via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web_proxy DynamicSecretK8S#secure_access_web_proxy}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#tags DynamicSecretK8S#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#target_name DynamicSecretK8S#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#user_ttl DynamicSecretK8S#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5b2e9649aa094120d16a9c4ce9ffa75d1e5ca20f8ebeb90ac75259ebc5952a1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretK8SConfig(
            name=name,
            custom_username_template=custom_username_template,
            delete_protection=delete_protection,
            encryption_key_name=encryption_key_name,
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
        '''Generates CDKTF code for importing a DynamicSecretK8S resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretK8S to import.
        :param import_from_id: The id of the existing DynamicSecretK8S that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretK8S to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee8981639e6a5861c411353ee80aec30ecba308cf274f0e68b20ade07732785e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomUsernameTemplate")
    def reset_custom_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUsernameTemplate", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

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
    @jsii.member(jsii_name="customUsernameTemplateInput")
    def custom_username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customUsernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyNameInput")
    def encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKeyNameInput"))

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
    @jsii.member(jsii_name="customUsernameTemplate")
    def custom_username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customUsernameTemplate"))

    @custom_username_template.setter
    def custom_username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaf13e69ebf6c45dcc7abd534677265c7fc954894a21561c6382d71f6a145f29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customUsernameTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b758dea95bc40965ca14ee8017044edf82aca0fd5d2ea3da4bd7dd2f9e25b16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b95e8db5b6724246fc7c709066b5d97800877f3d4c1f907ec696d4ed3b3991b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c584f3b66b35959657685345d8a9bc8230feb0845f64196932ffa0b06a77caf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="k8SAllowedNamespaces")
    def k8_s_allowed_namespaces(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SAllowedNamespaces"))

    @k8_s_allowed_namespaces.setter
    def k8_s_allowed_namespaces(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ced43d8e3b7c5d07ed99d2ac030f731f3f5cd0113a54f1035d8c4eeb7ffec2c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SAllowedNamespaces", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClusterCaCert")
    def k8_s_cluster_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClusterCaCert"))

    @k8_s_cluster_ca_cert.setter
    def k8_s_cluster_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e95c8c551e24c8ade55a4168e54425da73e8f185f261de148d7f94fa0f8bc29)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClusterCaCert", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClusterEndpoint")
    def k8_s_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClusterEndpoint"))

    @k8_s_cluster_endpoint.setter
    def k8_s_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a60123e4e98a83f86ada8bdf280f19b5c3d37ee00d0f9df63b33215abc90c77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClusterToken")
    def k8_s_cluster_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClusterToken"))

    @k8_s_cluster_token.setter
    def k8_s_cluster_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7f438de6c935e346be67f6ff4759a0613c66c71054f0e06405b44ab92b24c42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClusterToken", value)

    @builtins.property
    @jsii.member(jsii_name="k8SNamespace")
    def k8_s_namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SNamespace"))

    @k8_s_namespace.setter
    def k8_s_namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c6c781ef37c8fec5e597834b3414643e38187e0bd68b0189d2d41f44aedbd00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SNamespace", value)

    @builtins.property
    @jsii.member(jsii_name="k8SPredefinedRoleName")
    def k8_s_predefined_role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SPredefinedRoleName"))

    @k8_s_predefined_role_name.setter
    def k8_s_predefined_role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdf5e982f54e042c9377632bf349995bb9cb95188e4277b1a6e1a144c353bfde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SPredefinedRoleName", value)

    @builtins.property
    @jsii.member(jsii_name="k8SPredefinedRoleType")
    def k8_s_predefined_role_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SPredefinedRoleType"))

    @k8_s_predefined_role_type.setter
    def k8_s_predefined_role_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1a55cf4a1e36ba1ea8703ae228e64feee05bdd26e5307c4c2aaf842abaea32e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SPredefinedRoleType", value)

    @builtins.property
    @jsii.member(jsii_name="k8SServiceAccount")
    def k8_s_service_account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SServiceAccount"))

    @k8_s_service_account.setter
    def k8_s_service_account(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00ad54b764d18ef2bff2baa08fec1be0acd6e620a697ce7ba2c5292186ab41ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SServiceAccount", value)

    @builtins.property
    @jsii.member(jsii_name="k8SServiceAccountType")
    def k8_s_service_account_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SServiceAccountType"))

    @k8_s_service_account_type.setter
    def k8_s_service_account_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__103c7e71df7479d1824c5d06de200a65388fdf3cec3c308484488afe7d9e7cef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SServiceAccountType", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c33dd5a76434ed9cffe02122e1b8955ca02f129f76ebbbca76631721e8332af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8317cee7f12929acd9d621d10561b3df1a6672f414fe6e669c29d5e58e6a735f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessAllowPortForwading", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fde9645606e2ecb59403424e2e5e49ca7511d2877a90ef765c6606cae0265b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessClusterEndpoint")
    def secure_access_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessClusterEndpoint"))

    @secure_access_cluster_endpoint.setter
    def secure_access_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__726211166f89609569102e234a8c0443ae649680b593247a11e6207a301fa711)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDashboardUrl")
    def secure_access_dashboard_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDashboardUrl"))

    @secure_access_dashboard_url.setter
    def secure_access_dashboard_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69bbb8f825c2ea46ef825f1430c7251791caf0d0ba2d3a8b0043f9cdc4fd4db7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDashboardUrl", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f45fd801ad6699f3f4919a89b62ffab333ecfd2060d8e979bfc83b64cd578792)
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
            type_hints = typing.get_type_hints(_typecheckingstub__21f423a7d48a389fab5d82559f9f4c656c80189e8f58e3f4fc74b71a248cde8e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__503dc6d5675f48fd15dc418a24f86212236220c64eb7df02404ab0db9308f534)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fec6487d65ab862c65b958f7a795bcbeb10257b8a90a011db0678ef1badd429e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWebProxy", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eab5a6833d99684cbb56afa9e52edf8f6564a21fce33c0a4f557c02553c1225)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c586df95c3b197b9e15877d61a26add13e47c81df4eb3e60db5431e3a7c4b667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__470018a45f41e52bb0728cc63074daf179d0c4c1117d46a519478e2d0ce03cc8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretK8S.DynamicSecretK8SConfig",
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
        "custom_username_template": "customUsernameTemplate",
        "delete_protection": "deleteProtection",
        "encryption_key_name": "encryptionKeyName",
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
class DynamicSecretK8SConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        custom_username_template: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#name DynamicSecretK8S#name}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#custom_username_template DynamicSecretK8S#custom_username_template}
        :param delete_protection: Protection from accidental deletion of this item [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#delete_protection DynamicSecretK8S#delete_protection}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#encryption_key_name DynamicSecretK8S#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#id DynamicSecretK8S#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param k8_s_allowed_namespaces: Comma-separated list of allowed K8S namespaces for the generated ServiceAccount (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_allowed_namespaces DynamicSecretK8S#k8s_allowed_namespaces}
        :param k8_s_cluster_ca_cert: K8S Cluster certificate. Base 64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_ca_cert DynamicSecretK8S#k8s_cluster_ca_cert}
        :param k8_s_cluster_endpoint: K8S Cluster endpoint. https:// , <DNS / IP> of the cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_endpoint DynamicSecretK8S#k8s_cluster_endpoint}
        :param k8_s_cluster_token: K8S Cluster authentication token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_token DynamicSecretK8S#k8s_cluster_token}
        :param k8_s_namespace: K8S Namespace where the ServiceAccount exists. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_namespace DynamicSecretK8S#k8s_namespace}
        :param k8_s_predefined_role_name: The pre-existing Role or ClusterRole name to bind the generated ServiceAccount to (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_predefined_role_name DynamicSecretK8S#k8s_predefined_role_name}
        :param k8_s_predefined_role_type: Specifies the type of the pre-existing K8S role [Role, ClusterRole] (relevant only for k8s-service-account-type=dynamic). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_predefined_role_type DynamicSecretK8S#k8s_predefined_role_type}
        :param k8_s_service_account: K8S ServiceAccount to extract token from. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_service_account DynamicSecretK8S#k8s_service_account}
        :param k8_s_service_account_type: K8S ServiceAccount type [fixed, dynamic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_service_account_type DynamicSecretK8S#k8s_service_account_type}
        :param secure_access_allow_port_forwading: Enable Port forwarding while using CLI access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_allow_port_forwading DynamicSecretK8S#secure_access_allow_port_forwading}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_bastion_issuer DynamicSecretK8S#secure_access_bastion_issuer}
        :param secure_access_cluster_endpoint: The K8s cluster endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_cluster_endpoint DynamicSecretK8S#secure_access_cluster_endpoint}
        :param secure_access_dashboard_url: The K8s dashboard url. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_dashboard_url DynamicSecretK8S#secure_access_dashboard_url}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_enable DynamicSecretK8S#secure_access_enable}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web DynamicSecretK8S#secure_access_web}
        :param secure_access_web_browsing: Secure browser via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web_browsing DynamicSecretK8S#secure_access_web_browsing}
        :param secure_access_web_proxy: Web-Proxy via Akeyless Web Access Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web_proxy DynamicSecretK8S#secure_access_web_proxy}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#tags DynamicSecretK8S#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#target_name DynamicSecretK8S#target_name}
        :param user_ttl: User TTL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#user_ttl DynamicSecretK8S#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bf5197b6bcb70f021f0430c39be4c8e9af0fc5b5130b78b6a41b8b63b6d0c9b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument custom_username_template", value=custom_username_template, expected_type=type_hints["custom_username_template"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
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
        if custom_username_template is not None:
            self._values["custom_username_template"] = custom_username_template
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
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
        '''Dynamic secret name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#name DynamicSecretK8S#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_username_template(self) -> typing.Optional[builtins.str]:
        '''Customize how temporary usernames are generated using go template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#custom_username_template DynamicSecretK8S#custom_username_template}
        '''
        result = self._values.get("custom_username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this item [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#delete_protection DynamicSecretK8S#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#encryption_key_name DynamicSecretK8S#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#id DynamicSecretK8S#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_allowed_namespaces(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of allowed K8S namespaces for the generated ServiceAccount (relevant only for k8s-service-account-type=dynamic).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_allowed_namespaces DynamicSecretK8S#k8s_allowed_namespaces}
        '''
        result = self._values.get("k8_s_allowed_namespaces")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_cluster_ca_cert(self) -> typing.Optional[builtins.str]:
        '''K8S Cluster certificate. Base 64 encoded certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_ca_cert DynamicSecretK8S#k8s_cluster_ca_cert}
        '''
        result = self._values.get("k8_s_cluster_ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''K8S Cluster endpoint. https:// , <DNS / IP> of the cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_endpoint DynamicSecretK8S#k8s_cluster_endpoint}
        '''
        result = self._values.get("k8_s_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_cluster_token(self) -> typing.Optional[builtins.str]:
        '''K8S Cluster authentication token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_cluster_token DynamicSecretK8S#k8s_cluster_token}
        '''
        result = self._values.get("k8_s_cluster_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_namespace(self) -> typing.Optional[builtins.str]:
        '''K8S Namespace where the ServiceAccount exists.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_namespace DynamicSecretK8S#k8s_namespace}
        '''
        result = self._values.get("k8_s_namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_predefined_role_name(self) -> typing.Optional[builtins.str]:
        '''The pre-existing Role or ClusterRole name to bind the generated ServiceAccount to (relevant only for k8s-service-account-type=dynamic).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_predefined_role_name DynamicSecretK8S#k8s_predefined_role_name}
        '''
        result = self._values.get("k8_s_predefined_role_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_predefined_role_type(self) -> typing.Optional[builtins.str]:
        '''Specifies the type of the pre-existing K8S role [Role, ClusterRole] (relevant only for k8s-service-account-type=dynamic).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_predefined_role_type DynamicSecretK8S#k8s_predefined_role_type}
        '''
        result = self._values.get("k8_s_predefined_role_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_service_account(self) -> typing.Optional[builtins.str]:
        '''K8S ServiceAccount to extract token from.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_service_account DynamicSecretK8S#k8s_service_account}
        '''
        result = self._values.get("k8_s_service_account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_service_account_type(self) -> typing.Optional[builtins.str]:
        '''K8S ServiceAccount type [fixed, dynamic].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#k8s_service_account_type DynamicSecretK8S#k8s_service_account_type}
        '''
        result = self._values.get("k8_s_service_account_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_allow_port_forwading(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Port forwarding while using CLI access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_allow_port_forwading DynamicSecretK8S#secure_access_allow_port_forwading}
        '''
        result = self._values.get("secure_access_allow_port_forwading")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_bastion_issuer DynamicSecretK8S#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''The K8s cluster endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_cluster_endpoint DynamicSecretK8S#secure_access_cluster_endpoint}
        '''
        result = self._values.get("secure_access_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_dashboard_url(self) -> typing.Optional[builtins.str]:
        '''The K8s dashboard url.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_dashboard_url DynamicSecretK8S#secure_access_dashboard_url}
        '''
        result = self._values.get("secure_access_dashboard_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_enable DynamicSecretK8S#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web DynamicSecretK8S#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_web_browsing(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Secure browser via Akeyless Web Access Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web_browsing DynamicSecretK8S#secure_access_web_browsing}
        '''
        result = self._values.get("secure_access_web_browsing")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def secure_access_web_proxy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Web-Proxy via Akeyless Web Access Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#secure_access_web_proxy DynamicSecretK8S#secure_access_web_proxy}
        '''
        result = self._values.get("secure_access_web_proxy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#tags DynamicSecretK8S#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#target_name DynamicSecretK8S#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_k8s#user_ttl DynamicSecretK8S#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretK8SConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretK8S",
    "DynamicSecretK8SConfig",
]

publication.publish()

def _typecheckingstub__e5b2e9649aa094120d16a9c4ce9ffa75d1e5ca20f8ebeb90ac75259ebc5952a1(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    custom_username_template: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__ee8981639e6a5861c411353ee80aec30ecba308cf274f0e68b20ade07732785e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaf13e69ebf6c45dcc7abd534677265c7fc954894a21561c6382d71f6a145f29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b758dea95bc40965ca14ee8017044edf82aca0fd5d2ea3da4bd7dd2f9e25b16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b95e8db5b6724246fc7c709066b5d97800877f3d4c1f907ec696d4ed3b3991b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c584f3b66b35959657685345d8a9bc8230feb0845f64196932ffa0b06a77caf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ced43d8e3b7c5d07ed99d2ac030f731f3f5cd0113a54f1035d8c4eeb7ffec2c2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e95c8c551e24c8ade55a4168e54425da73e8f185f261de148d7f94fa0f8bc29(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a60123e4e98a83f86ada8bdf280f19b5c3d37ee00d0f9df63b33215abc90c77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7f438de6c935e346be67f6ff4759a0613c66c71054f0e06405b44ab92b24c42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c6c781ef37c8fec5e597834b3414643e38187e0bd68b0189d2d41f44aedbd00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdf5e982f54e042c9377632bf349995bb9cb95188e4277b1a6e1a144c353bfde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1a55cf4a1e36ba1ea8703ae228e64feee05bdd26e5307c4c2aaf842abaea32e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00ad54b764d18ef2bff2baa08fec1be0acd6e620a697ce7ba2c5292186ab41ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__103c7e71df7479d1824c5d06de200a65388fdf3cec3c308484488afe7d9e7cef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c33dd5a76434ed9cffe02122e1b8955ca02f129f76ebbbca76631721e8332af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8317cee7f12929acd9d621d10561b3df1a6672f414fe6e669c29d5e58e6a735f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fde9645606e2ecb59403424e2e5e49ca7511d2877a90ef765c6606cae0265b0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__726211166f89609569102e234a8c0443ae649680b593247a11e6207a301fa711(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69bbb8f825c2ea46ef825f1430c7251791caf0d0ba2d3a8b0043f9cdc4fd4db7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f45fd801ad6699f3f4919a89b62ffab333ecfd2060d8e979bfc83b64cd578792(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21f423a7d48a389fab5d82559f9f4c656c80189e8f58e3f4fc74b71a248cde8e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__503dc6d5675f48fd15dc418a24f86212236220c64eb7df02404ab0db9308f534(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fec6487d65ab862c65b958f7a795bcbeb10257b8a90a011db0678ef1badd429e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eab5a6833d99684cbb56afa9e52edf8f6564a21fce33c0a4f557c02553c1225(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c586df95c3b197b9e15877d61a26add13e47c81df4eb3e60db5431e3a7c4b667(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__470018a45f41e52bb0728cc63074daf179d0c4c1117d46a519478e2d0ce03cc8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bf5197b6bcb70f021f0430c39be4c8e9af0fc5b5130b78b6a41b8b63b6d0c9b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    custom_username_template: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
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
