'''
# `akeyless_k8s_auth_config`

Refer to the Terraform Registry for docs: [`akeyless_k8s_auth_config`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config).
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


class K8SAuthConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.k8SAuthConfig.K8SAuthConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config akeyless_k8s_auth_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        access_id: builtins.str,
        name: builtins.str,
        cluster_api_type: typing.Optional[builtins.str] = None,
        disable_issuer_validation: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        k8_s_auth_type: typing.Optional[builtins.str] = None,
        k8_s_ca_cert: typing.Optional[builtins.str] = None,
        k8_s_client_certificate: typing.Optional[builtins.str] = None,
        k8_s_client_key: typing.Optional[builtins.str] = None,
        k8_s_host: typing.Optional[builtins.str] = None,
        k8_s_issuer: typing.Optional[builtins.str] = None,
        rancher_api_key: typing.Optional[builtins.str] = None,
        rancher_cluster_id: typing.Optional[builtins.str] = None,
        signing_key: typing.Optional[builtins.str] = None,
        token_exp: typing.Optional[jsii.Number] = None,
        token_reviewer_jwt: typing.Optional[builtins.str] = None,
        use_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config akeyless_k8s_auth_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param access_id: The access ID of the Kubernetes auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#access_id K8SAuthConfig#access_id}
        :param name: K8S Auth config name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#name K8SAuthConfig#name}
        :param cluster_api_type: Cluster access type. options: [native_k8s, rancher]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#cluster_api_type K8SAuthConfig#cluster_api_type}
        :param disable_issuer_validation: Disable issuer validation [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#disable_issuer_validation K8SAuthConfig#disable_issuer_validation}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#id K8SAuthConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param k8_s_auth_type: Native K8S auth type, [token/certificate]. (relevant for native_k8s only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_auth_type K8SAuthConfig#k8s_auth_type}
        :param k8_s_ca_cert: The CA Certificate (base64 encoded) to use to call into the kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_ca_cert K8SAuthConfig#k8s_ca_cert}
        :param k8_s_client_certificate: Content of the k8 client certificate (PEM format) in a Base64 format (relevant for native_k8s only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_client_certificate K8SAuthConfig#k8s_client_certificate}
        :param k8_s_client_key: Content of the k8 client private key (PEM format) in a Base64 format (relevant for native_k8s only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_client_key K8SAuthConfig#k8s_client_key}
        :param k8_s_host: The URL of the kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_host K8SAuthConfig#k8s_host}
        :param k8_s_issuer: The Kubernetes JWT issuer name. If not set, this <kubernetes/serviceaccount> will be used by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_issuer K8SAuthConfig#k8s_issuer}
        :param rancher_api_key: The api key used to access the TokenReview API to validate other JWTs (relevant for rancher only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#rancher_api_key K8SAuthConfig#rancher_api_key}
        :param rancher_cluster_id: The cluster id as define in rancher (relevant for rancher only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#rancher_cluster_id K8SAuthConfig#rancher_cluster_id}
        :param signing_key: The private key (in base64 encoded of the PEM format) associated with the public key defined in the Kubernetes auth. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#signing_key K8SAuthConfig#signing_key}
        :param token_exp: Time in seconds of expiration of the Akeyless Kube Auth Method token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#token_exp K8SAuthConfig#token_exp}
        :param token_reviewer_jwt: A Kubernetes service account JWT used to access the TokenReview API to validate other JWTs. If not set, the JWT submitted in the authentication process will be used to access the Kubernetes TokenReview API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#token_reviewer_jwt K8SAuthConfig#token_reviewer_jwt}
        :param use_local_ca_jwt: Use the GW's service account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#use_local_ca_jwt K8SAuthConfig#use_local_ca_jwt}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f36c903400503b2e39d725e7eea8ec0fc5b937ca689cfe6a8572c0fb5590598)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = K8SAuthConfigConfig(
            access_id=access_id,
            name=name,
            cluster_api_type=cluster_api_type,
            disable_issuer_validation=disable_issuer_validation,
            id=id,
            k8_s_auth_type=k8_s_auth_type,
            k8_s_ca_cert=k8_s_ca_cert,
            k8_s_client_certificate=k8_s_client_certificate,
            k8_s_client_key=k8_s_client_key,
            k8_s_host=k8_s_host,
            k8_s_issuer=k8_s_issuer,
            rancher_api_key=rancher_api_key,
            rancher_cluster_id=rancher_cluster_id,
            signing_key=signing_key,
            token_exp=token_exp,
            token_reviewer_jwt=token_reviewer_jwt,
            use_local_ca_jwt=use_local_ca_jwt,
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
        '''Generates CDKTF code for importing a K8SAuthConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the K8SAuthConfig to import.
        :param import_from_id: The id of the existing K8SAuthConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the K8SAuthConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4012f9fcca8da293d03a0a7c5e03ee43370922366a0392568cf260cd5b6b4188)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetClusterApiType")
    def reset_cluster_api_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterApiType", []))

    @jsii.member(jsii_name="resetDisableIssuerValidation")
    def reset_disable_issuer_validation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableIssuerValidation", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetK8SAuthType")
    def reset_k8_s_auth_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SAuthType", []))

    @jsii.member(jsii_name="resetK8SCaCert")
    def reset_k8_s_ca_cert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SCaCert", []))

    @jsii.member(jsii_name="resetK8SClientCertificate")
    def reset_k8_s_client_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SClientCertificate", []))

    @jsii.member(jsii_name="resetK8SClientKey")
    def reset_k8_s_client_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SClientKey", []))

    @jsii.member(jsii_name="resetK8SHost")
    def reset_k8_s_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SHost", []))

    @jsii.member(jsii_name="resetK8SIssuer")
    def reset_k8_s_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK8SIssuer", []))

    @jsii.member(jsii_name="resetRancherApiKey")
    def reset_rancher_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRancherApiKey", []))

    @jsii.member(jsii_name="resetRancherClusterId")
    def reset_rancher_cluster_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRancherClusterId", []))

    @jsii.member(jsii_name="resetSigningKey")
    def reset_signing_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSigningKey", []))

    @jsii.member(jsii_name="resetTokenExp")
    def reset_token_exp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenExp", []))

    @jsii.member(jsii_name="resetTokenReviewerJwt")
    def reset_token_reviewer_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenReviewerJwt", []))

    @jsii.member(jsii_name="resetUseLocalCaJwt")
    def reset_use_local_ca_jwt(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseLocalCaJwt", []))

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
    @jsii.member(jsii_name="accessIdInput")
    def access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterApiTypeInput")
    def cluster_api_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterApiTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="disableIssuerValidationInput")
    def disable_issuer_validation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "disableIssuerValidationInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SAuthTypeInput")
    def k8_s_auth_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SAuthTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SCaCertInput")
    def k8_s_ca_cert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SCaCertInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SClientCertificateInput")
    def k8_s_client_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SClientCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SClientKeyInput")
    def k8_s_client_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SClientKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SHostInput")
    def k8_s_host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SHostInput"))

    @builtins.property
    @jsii.member(jsii_name="k8SIssuerInput")
    def k8_s_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "k8SIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="rancherApiKeyInput")
    def rancher_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rancherApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="rancherClusterIdInput")
    def rancher_cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rancherClusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="signingKeyInput")
    def signing_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "signingKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenExpInput")
    def token_exp_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokenExpInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenReviewerJwtInput")
    def token_reviewer_jwt_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenReviewerJwtInput"))

    @builtins.property
    @jsii.member(jsii_name="useLocalCaJwtInput")
    def use_local_ca_jwt_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useLocalCaJwtInput"))

    @builtins.property
    @jsii.member(jsii_name="accessId")
    def access_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessId"))

    @access_id.setter
    def access_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77777c6a86e5497f17f042c4d597a0bb7953517754d8dac7e2939414fb58de56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessId", value)

    @builtins.property
    @jsii.member(jsii_name="clusterApiType")
    def cluster_api_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterApiType"))

    @cluster_api_type.setter
    def cluster_api_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0045496f88193904a8a0de845cc0cfd4118e7611954936b6e97be8ea0d7ea1a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterApiType", value)

    @builtins.property
    @jsii.member(jsii_name="disableIssuerValidation")
    def disable_issuer_validation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "disableIssuerValidation"))

    @disable_issuer_validation.setter
    def disable_issuer_validation(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8770f60b71fd82b4617f9d5682bbeffe6d84c898cd4cc15e454eac9729c62f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableIssuerValidation", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e73447394970ee5d8a23f7926efd50100de6f6a950984433762e67b22f362d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="k8SAuthType")
    def k8_s_auth_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SAuthType"))

    @k8_s_auth_type.setter
    def k8_s_auth_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e60bfabd7e004a7c864a0c0938395d69626d9be2d9667c7c4a9a9d320dbeb52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SAuthType", value)

    @builtins.property
    @jsii.member(jsii_name="k8SCaCert")
    def k8_s_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SCaCert"))

    @k8_s_ca_cert.setter
    def k8_s_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__111603bea9fa8e418902e37a3ca5f80dfc34b54754bd947fba9417aedc4d850f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SCaCert", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClientCertificate")
    def k8_s_client_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClientCertificate"))

    @k8_s_client_certificate.setter
    def k8_s_client_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcd84b87d8aae7dcd37bd742e91686b658e22f03d278569825fe90818e2f4e7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClientCertificate", value)

    @builtins.property
    @jsii.member(jsii_name="k8SClientKey")
    def k8_s_client_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SClientKey"))

    @k8_s_client_key.setter
    def k8_s_client_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c46a36e65facb54101ee52f46c4c5e0501932683a7b2b0d88379c748557a692a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SClientKey", value)

    @builtins.property
    @jsii.member(jsii_name="k8SHost")
    def k8_s_host(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SHost"))

    @k8_s_host.setter
    def k8_s_host(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0483dce894e94706ebb15110d21b40b966642694f1f3da4440cfa0e9d37025a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SHost", value)

    @builtins.property
    @jsii.member(jsii_name="k8SIssuer")
    def k8_s_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "k8SIssuer"))

    @k8_s_issuer.setter
    def k8_s_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f89def4553304d8305b82003f79e1ed34b94dab1c5716e403b47db122250050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k8SIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__348522fe47f78c00df1ac186b663eb0c1417ce27fc108930a04bdbbae09451e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="rancherApiKey")
    def rancher_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rancherApiKey"))

    @rancher_api_key.setter
    def rancher_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5b809fbc909a6f29d9478a53090bff1e7947b4f1970b94b7a2ea9e78c0a25e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rancherApiKey", value)

    @builtins.property
    @jsii.member(jsii_name="rancherClusterId")
    def rancher_cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rancherClusterId"))

    @rancher_cluster_id.setter
    def rancher_cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97f6c00d09af3e53eb9b40633860385f6b86de7bc597fad87d23deab1e5267fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rancherClusterId", value)

    @builtins.property
    @jsii.member(jsii_name="signingKey")
    def signing_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signingKey"))

    @signing_key.setter
    def signing_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59ccde929e195581aed40c1e408ee49fbb53db2ce619b03d21dd04f0de9aff65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "signingKey", value)

    @builtins.property
    @jsii.member(jsii_name="tokenExp")
    def token_exp(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokenExp"))

    @token_exp.setter
    def token_exp(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac7cb00db981ff5a812a0b3287e22260bb1c917ef05e6ae28ec51f2346c13cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenExp", value)

    @builtins.property
    @jsii.member(jsii_name="tokenReviewerJwt")
    def token_reviewer_jwt(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenReviewerJwt"))

    @token_reviewer_jwt.setter
    def token_reviewer_jwt(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f4da0766ae45a6ceec440e8e9e7910c0251576345c13ba7b00a23bc3f747d0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenReviewerJwt", value)

    @builtins.property
    @jsii.member(jsii_name="useLocalCaJwt")
    def use_local_ca_jwt(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useLocalCaJwt"))

    @use_local_ca_jwt.setter
    def use_local_ca_jwt(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bdf1d787df56564dbc3614ce74e3f3901270268d57ef2d93bdf3b11a87244a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useLocalCaJwt", value)


@jsii.data_type(
    jsii_type="akeyless.k8SAuthConfig.K8SAuthConfigConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "access_id": "accessId",
        "name": "name",
        "cluster_api_type": "clusterApiType",
        "disable_issuer_validation": "disableIssuerValidation",
        "id": "id",
        "k8_s_auth_type": "k8SAuthType",
        "k8_s_ca_cert": "k8SCaCert",
        "k8_s_client_certificate": "k8SClientCertificate",
        "k8_s_client_key": "k8SClientKey",
        "k8_s_host": "k8SHost",
        "k8_s_issuer": "k8SIssuer",
        "rancher_api_key": "rancherApiKey",
        "rancher_cluster_id": "rancherClusterId",
        "signing_key": "signingKey",
        "token_exp": "tokenExp",
        "token_reviewer_jwt": "tokenReviewerJwt",
        "use_local_ca_jwt": "useLocalCaJwt",
    },
)
class K8SAuthConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        access_id: builtins.str,
        name: builtins.str,
        cluster_api_type: typing.Optional[builtins.str] = None,
        disable_issuer_validation: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        k8_s_auth_type: typing.Optional[builtins.str] = None,
        k8_s_ca_cert: typing.Optional[builtins.str] = None,
        k8_s_client_certificate: typing.Optional[builtins.str] = None,
        k8_s_client_key: typing.Optional[builtins.str] = None,
        k8_s_host: typing.Optional[builtins.str] = None,
        k8_s_issuer: typing.Optional[builtins.str] = None,
        rancher_api_key: typing.Optional[builtins.str] = None,
        rancher_cluster_id: typing.Optional[builtins.str] = None,
        signing_key: typing.Optional[builtins.str] = None,
        token_exp: typing.Optional[jsii.Number] = None,
        token_reviewer_jwt: typing.Optional[builtins.str] = None,
        use_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param access_id: The access ID of the Kubernetes auth method. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#access_id K8SAuthConfig#access_id}
        :param name: K8S Auth config name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#name K8SAuthConfig#name}
        :param cluster_api_type: Cluster access type. options: [native_k8s, rancher]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#cluster_api_type K8SAuthConfig#cluster_api_type}
        :param disable_issuer_validation: Disable issuer validation [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#disable_issuer_validation K8SAuthConfig#disable_issuer_validation}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#id K8SAuthConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param k8_s_auth_type: Native K8S auth type, [token/certificate]. (relevant for native_k8s only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_auth_type K8SAuthConfig#k8s_auth_type}
        :param k8_s_ca_cert: The CA Certificate (base64 encoded) to use to call into the kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_ca_cert K8SAuthConfig#k8s_ca_cert}
        :param k8_s_client_certificate: Content of the k8 client certificate (PEM format) in a Base64 format (relevant for native_k8s only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_client_certificate K8SAuthConfig#k8s_client_certificate}
        :param k8_s_client_key: Content of the k8 client private key (PEM format) in a Base64 format (relevant for native_k8s only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_client_key K8SAuthConfig#k8s_client_key}
        :param k8_s_host: The URL of the kubernetes API server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_host K8SAuthConfig#k8s_host}
        :param k8_s_issuer: The Kubernetes JWT issuer name. If not set, this <kubernetes/serviceaccount> will be used by default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_issuer K8SAuthConfig#k8s_issuer}
        :param rancher_api_key: The api key used to access the TokenReview API to validate other JWTs (relevant for rancher only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#rancher_api_key K8SAuthConfig#rancher_api_key}
        :param rancher_cluster_id: The cluster id as define in rancher (relevant for rancher only). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#rancher_cluster_id K8SAuthConfig#rancher_cluster_id}
        :param signing_key: The private key (in base64 encoded of the PEM format) associated with the public key defined in the Kubernetes auth. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#signing_key K8SAuthConfig#signing_key}
        :param token_exp: Time in seconds of expiration of the Akeyless Kube Auth Method token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#token_exp K8SAuthConfig#token_exp}
        :param token_reviewer_jwt: A Kubernetes service account JWT used to access the TokenReview API to validate other JWTs. If not set, the JWT submitted in the authentication process will be used to access the Kubernetes TokenReview API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#token_reviewer_jwt K8SAuthConfig#token_reviewer_jwt}
        :param use_local_ca_jwt: Use the GW's service account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#use_local_ca_jwt K8SAuthConfig#use_local_ca_jwt}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac0496a10afb346ed7f939b901d192c9e8e0164e65e33168629e34f12a8cabc8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument access_id", value=access_id, expected_type=type_hints["access_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument cluster_api_type", value=cluster_api_type, expected_type=type_hints["cluster_api_type"])
            check_type(argname="argument disable_issuer_validation", value=disable_issuer_validation, expected_type=type_hints["disable_issuer_validation"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument k8_s_auth_type", value=k8_s_auth_type, expected_type=type_hints["k8_s_auth_type"])
            check_type(argname="argument k8_s_ca_cert", value=k8_s_ca_cert, expected_type=type_hints["k8_s_ca_cert"])
            check_type(argname="argument k8_s_client_certificate", value=k8_s_client_certificate, expected_type=type_hints["k8_s_client_certificate"])
            check_type(argname="argument k8_s_client_key", value=k8_s_client_key, expected_type=type_hints["k8_s_client_key"])
            check_type(argname="argument k8_s_host", value=k8_s_host, expected_type=type_hints["k8_s_host"])
            check_type(argname="argument k8_s_issuer", value=k8_s_issuer, expected_type=type_hints["k8_s_issuer"])
            check_type(argname="argument rancher_api_key", value=rancher_api_key, expected_type=type_hints["rancher_api_key"])
            check_type(argname="argument rancher_cluster_id", value=rancher_cluster_id, expected_type=type_hints["rancher_cluster_id"])
            check_type(argname="argument signing_key", value=signing_key, expected_type=type_hints["signing_key"])
            check_type(argname="argument token_exp", value=token_exp, expected_type=type_hints["token_exp"])
            check_type(argname="argument token_reviewer_jwt", value=token_reviewer_jwt, expected_type=type_hints["token_reviewer_jwt"])
            check_type(argname="argument use_local_ca_jwt", value=use_local_ca_jwt, expected_type=type_hints["use_local_ca_jwt"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access_id": access_id,
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
        if cluster_api_type is not None:
            self._values["cluster_api_type"] = cluster_api_type
        if disable_issuer_validation is not None:
            self._values["disable_issuer_validation"] = disable_issuer_validation
        if id is not None:
            self._values["id"] = id
        if k8_s_auth_type is not None:
            self._values["k8_s_auth_type"] = k8_s_auth_type
        if k8_s_ca_cert is not None:
            self._values["k8_s_ca_cert"] = k8_s_ca_cert
        if k8_s_client_certificate is not None:
            self._values["k8_s_client_certificate"] = k8_s_client_certificate
        if k8_s_client_key is not None:
            self._values["k8_s_client_key"] = k8_s_client_key
        if k8_s_host is not None:
            self._values["k8_s_host"] = k8_s_host
        if k8_s_issuer is not None:
            self._values["k8_s_issuer"] = k8_s_issuer
        if rancher_api_key is not None:
            self._values["rancher_api_key"] = rancher_api_key
        if rancher_cluster_id is not None:
            self._values["rancher_cluster_id"] = rancher_cluster_id
        if signing_key is not None:
            self._values["signing_key"] = signing_key
        if token_exp is not None:
            self._values["token_exp"] = token_exp
        if token_reviewer_jwt is not None:
            self._values["token_reviewer_jwt"] = token_reviewer_jwt
        if use_local_ca_jwt is not None:
            self._values["use_local_ca_jwt"] = use_local_ca_jwt

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
    def access_id(self) -> builtins.str:
        '''The access ID of the Kubernetes auth method.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#access_id K8SAuthConfig#access_id}
        '''
        result = self._values.get("access_id")
        assert result is not None, "Required property 'access_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''K8S Auth config name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#name K8SAuthConfig#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster_api_type(self) -> typing.Optional[builtins.str]:
        '''Cluster access type. options: [native_k8s, rancher].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#cluster_api_type K8SAuthConfig#cluster_api_type}
        '''
        result = self._values.get("cluster_api_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_issuer_validation(self) -> typing.Optional[builtins.str]:
        '''Disable issuer validation [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#disable_issuer_validation K8SAuthConfig#disable_issuer_validation}
        '''
        result = self._values.get("disable_issuer_validation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#id K8SAuthConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_auth_type(self) -> typing.Optional[builtins.str]:
        '''Native K8S auth type, [token/certificate]. (relevant for native_k8s only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_auth_type K8SAuthConfig#k8s_auth_type}
        '''
        result = self._values.get("k8_s_auth_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_ca_cert(self) -> typing.Optional[builtins.str]:
        '''The CA Certificate (base64 encoded) to use to call into the kubernetes API server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_ca_cert K8SAuthConfig#k8s_ca_cert}
        '''
        result = self._values.get("k8_s_ca_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_client_certificate(self) -> typing.Optional[builtins.str]:
        '''Content of the k8 client certificate (PEM format) in a Base64 format (relevant for native_k8s only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_client_certificate K8SAuthConfig#k8s_client_certificate}
        '''
        result = self._values.get("k8_s_client_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_client_key(self) -> typing.Optional[builtins.str]:
        '''Content of the k8 client private key (PEM format) in a Base64 format (relevant for native_k8s only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_client_key K8SAuthConfig#k8s_client_key}
        '''
        result = self._values.get("k8_s_client_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_host(self) -> typing.Optional[builtins.str]:
        '''The URL of the kubernetes API server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_host K8SAuthConfig#k8s_host}
        '''
        result = self._values.get("k8_s_host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k8_s_issuer(self) -> typing.Optional[builtins.str]:
        '''The Kubernetes JWT issuer name. If not set, this <kubernetes/serviceaccount> will be used by default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#k8s_issuer K8SAuthConfig#k8s_issuer}
        '''
        result = self._values.get("k8_s_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rancher_api_key(self) -> typing.Optional[builtins.str]:
        '''The api key used to access the TokenReview API to validate other JWTs (relevant for rancher only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#rancher_api_key K8SAuthConfig#rancher_api_key}
        '''
        result = self._values.get("rancher_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rancher_cluster_id(self) -> typing.Optional[builtins.str]:
        '''The cluster id as define in rancher (relevant for rancher only).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#rancher_cluster_id K8SAuthConfig#rancher_cluster_id}
        '''
        result = self._values.get("rancher_cluster_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def signing_key(self) -> typing.Optional[builtins.str]:
        '''The private key (in base64 encoded of the PEM format) associated with the public key defined in the Kubernetes auth.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#signing_key K8SAuthConfig#signing_key}
        '''
        result = self._values.get("signing_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token_exp(self) -> typing.Optional[jsii.Number]:
        '''Time in seconds of expiration of the Akeyless Kube Auth Method token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#token_exp K8SAuthConfig#token_exp}
        '''
        result = self._values.get("token_exp")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def token_reviewer_jwt(self) -> typing.Optional[builtins.str]:
        '''A Kubernetes service account JWT used to access the TokenReview API to validate other JWTs.

        If not set, the JWT submitted in the authentication process will be used to access the Kubernetes TokenReview API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#token_reviewer_jwt K8SAuthConfig#token_reviewer_jwt}
        '''
        result = self._values.get("token_reviewer_jwt")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_local_ca_jwt(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use the GW's service account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/k8s_auth_config#use_local_ca_jwt K8SAuthConfig#use_local_ca_jwt}
        '''
        result = self._values.get("use_local_ca_jwt")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "K8SAuthConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "K8SAuthConfig",
    "K8SAuthConfigConfig",
]

publication.publish()

def _typecheckingstub__3f36c903400503b2e39d725e7eea8ec0fc5b937ca689cfe6a8572c0fb5590598(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    access_id: builtins.str,
    name: builtins.str,
    cluster_api_type: typing.Optional[builtins.str] = None,
    disable_issuer_validation: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    k8_s_auth_type: typing.Optional[builtins.str] = None,
    k8_s_ca_cert: typing.Optional[builtins.str] = None,
    k8_s_client_certificate: typing.Optional[builtins.str] = None,
    k8_s_client_key: typing.Optional[builtins.str] = None,
    k8_s_host: typing.Optional[builtins.str] = None,
    k8_s_issuer: typing.Optional[builtins.str] = None,
    rancher_api_key: typing.Optional[builtins.str] = None,
    rancher_cluster_id: typing.Optional[builtins.str] = None,
    signing_key: typing.Optional[builtins.str] = None,
    token_exp: typing.Optional[jsii.Number] = None,
    token_reviewer_jwt: typing.Optional[builtins.str] = None,
    use_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__4012f9fcca8da293d03a0a7c5e03ee43370922366a0392568cf260cd5b6b4188(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77777c6a86e5497f17f042c4d597a0bb7953517754d8dac7e2939414fb58de56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0045496f88193904a8a0de845cc0cfd4118e7611954936b6e97be8ea0d7ea1a4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8770f60b71fd82b4617f9d5682bbeffe6d84c898cd4cc15e454eac9729c62f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e73447394970ee5d8a23f7926efd50100de6f6a950984433762e67b22f362d9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e60bfabd7e004a7c864a0c0938395d69626d9be2d9667c7c4a9a9d320dbeb52(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__111603bea9fa8e418902e37a3ca5f80dfc34b54754bd947fba9417aedc4d850f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcd84b87d8aae7dcd37bd742e91686b658e22f03d278569825fe90818e2f4e7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c46a36e65facb54101ee52f46c4c5e0501932683a7b2b0d88379c748557a692a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0483dce894e94706ebb15110d21b40b966642694f1f3da4440cfa0e9d37025a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f89def4553304d8305b82003f79e1ed34b94dab1c5716e403b47db122250050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__348522fe47f78c00df1ac186b663eb0c1417ce27fc108930a04bdbbae09451e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5b809fbc909a6f29d9478a53090bff1e7947b4f1970b94b7a2ea9e78c0a25e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97f6c00d09af3e53eb9b40633860385f6b86de7bc597fad87d23deab1e5267fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59ccde929e195581aed40c1e408ee49fbb53db2ce619b03d21dd04f0de9aff65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac7cb00db981ff5a812a0b3287e22260bb1c917ef05e6ae28ec51f2346c13cb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f4da0766ae45a6ceec440e8e9e7910c0251576345c13ba7b00a23bc3f747d0e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bdf1d787df56564dbc3614ce74e3f3901270268d57ef2d93bdf3b11a87244a1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac0496a10afb346ed7f939b901d192c9e8e0164e65e33168629e34f12a8cabc8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    access_id: builtins.str,
    name: builtins.str,
    cluster_api_type: typing.Optional[builtins.str] = None,
    disable_issuer_validation: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    k8_s_auth_type: typing.Optional[builtins.str] = None,
    k8_s_ca_cert: typing.Optional[builtins.str] = None,
    k8_s_client_certificate: typing.Optional[builtins.str] = None,
    k8_s_client_key: typing.Optional[builtins.str] = None,
    k8_s_host: typing.Optional[builtins.str] = None,
    k8_s_issuer: typing.Optional[builtins.str] = None,
    rancher_api_key: typing.Optional[builtins.str] = None,
    rancher_cluster_id: typing.Optional[builtins.str] = None,
    signing_key: typing.Optional[builtins.str] = None,
    token_exp: typing.Optional[jsii.Number] = None,
    token_reviewer_jwt: typing.Optional[builtins.str] = None,
    use_local_ca_jwt: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
