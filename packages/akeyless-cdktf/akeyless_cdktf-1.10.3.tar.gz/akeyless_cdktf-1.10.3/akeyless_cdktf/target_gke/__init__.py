'''
# `akeyless_target_gke`

Refer to the Terraform Registry for docs: [`akeyless_target_gke`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke).
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


class TargetGke(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.targetGke.TargetGke",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke akeyless_target_gke}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        gke_account_key: typing.Optional[builtins.str] = None,
        gke_cluster_cert: typing.Optional[builtins.str] = None,
        gke_cluster_endpoint: typing.Optional[builtins.str] = None,
        gke_cluster_name: typing.Optional[builtins.str] = None,
        gke_service_account_email: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        use_gw_cloud_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke akeyless_target_gke} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#name TargetGke#name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#description TargetGke#description}
        :param gke_account_key: GKE service account key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_account_key TargetGke#gke_account_key}
        :param gke_cluster_cert: GKE Base-64 encoded cluster certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_cert TargetGke#gke_cluster_cert}
        :param gke_cluster_endpoint: GKE cluster endpoint, i.e., cluster URI https://<DNS/IP>. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_endpoint TargetGke#gke_cluster_endpoint}
        :param gke_cluster_name: GKE cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_name TargetGke#gke_cluster_name}
        :param gke_service_account_email: GKE service account email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_service_account_email TargetGke#gke_service_account_email}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#id TargetGke#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#key TargetGke#key}
        :param use_gw_cloud_identity: Use the GW's Cloud IAM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#use_gw_cloud_identity TargetGke#use_gw_cloud_identity}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96c1a442b9cddecf1809691c9d4eb9c95761cbfe5c105ecb9ec173a78cd4538c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TargetGkeConfig(
            name=name,
            description=description,
            gke_account_key=gke_account_key,
            gke_cluster_cert=gke_cluster_cert,
            gke_cluster_endpoint=gke_cluster_endpoint,
            gke_cluster_name=gke_cluster_name,
            gke_service_account_email=gke_service_account_email,
            id=id,
            key=key,
            use_gw_cloud_identity=use_gw_cloud_identity,
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
        '''Generates CDKTF code for importing a TargetGke resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TargetGke to import.
        :param import_from_id: The id of the existing TargetGke that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TargetGke to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d65775338b1a94ee0ddf252dc06590af8b7a250b20593588e62d0d88f834ce)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

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

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetUseGwCloudIdentity")
    def reset_use_gw_cloud_identity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseGwCloudIdentity", []))

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
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

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
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="useGwCloudIdentityInput")
    def use_gw_cloud_identity_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useGwCloudIdentityInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0721d4b69945ea407bccac5633a2c2cdb9f24444f3855f3085a3236cd8c2ce40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="gkeAccountKey")
    def gke_account_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeAccountKey"))

    @gke_account_key.setter
    def gke_account_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8018cf3ce5204175b2d9e5ce65d4a66204f2c16dc1a7fe45cdb23a0918b47df7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeAccountKey", value)

    @builtins.property
    @jsii.member(jsii_name="gkeClusterCert")
    def gke_cluster_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterCert"))

    @gke_cluster_cert.setter
    def gke_cluster_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45cafe2f47176ab07a2b54cf291a15d594140155a4f308c96f092b24fef81680)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterCert", value)

    @builtins.property
    @jsii.member(jsii_name="gkeClusterEndpoint")
    def gke_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterEndpoint"))

    @gke_cluster_endpoint.setter
    def gke_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e22208a803a30dd18d6bb8d4435db5e05f29475a142581ddf9032d4fd8197be5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="gkeClusterName")
    def gke_cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeClusterName"))

    @gke_cluster_name.setter
    def gke_cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b831df36ddb13d39c9deec0ea310840184d7a611b97d242f03106a6640a20a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeClusterName", value)

    @builtins.property
    @jsii.member(jsii_name="gkeServiceAccountEmail")
    def gke_service_account_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gkeServiceAccountEmail"))

    @gke_service_account_email.setter
    def gke_service_account_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19b87eb1cca6e85d680cba9192d211f94d555a45403cad52f6c59225a34b73f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gkeServiceAccountEmail", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df22c0430f1430bb56db5bab661047b70ae711e70bc017f40a74c1b214b6c8db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e8952475baa7ad880066ba741e455225bbd6b88fc196e9868b74749d9a0ea9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fb296b3e2643a62c013b1afe9bb9562582109fe6e9435abe5bd18ae2675eadd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="useGwCloudIdentity")
    def use_gw_cloud_identity(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useGwCloudIdentity"))

    @use_gw_cloud_identity.setter
    def use_gw_cloud_identity(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9be515bc468d28640e822a38bd5cf48b9aabccf8a4d893d69dc69e5de8f9ad7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useGwCloudIdentity", value)


@jsii.data_type(
    jsii_type="akeyless.targetGke.TargetGkeConfig",
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
        "description": "description",
        "gke_account_key": "gkeAccountKey",
        "gke_cluster_cert": "gkeClusterCert",
        "gke_cluster_endpoint": "gkeClusterEndpoint",
        "gke_cluster_name": "gkeClusterName",
        "gke_service_account_email": "gkeServiceAccountEmail",
        "id": "id",
        "key": "key",
        "use_gw_cloud_identity": "useGwCloudIdentity",
    },
)
class TargetGkeConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        description: typing.Optional[builtins.str] = None,
        gke_account_key: typing.Optional[builtins.str] = None,
        gke_cluster_cert: typing.Optional[builtins.str] = None,
        gke_cluster_endpoint: typing.Optional[builtins.str] = None,
        gke_cluster_name: typing.Optional[builtins.str] = None,
        gke_service_account_email: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        key: typing.Optional[builtins.str] = None,
        use_gw_cloud_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#name TargetGke#name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#description TargetGke#description}
        :param gke_account_key: GKE service account key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_account_key TargetGke#gke_account_key}
        :param gke_cluster_cert: GKE Base-64 encoded cluster certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_cert TargetGke#gke_cluster_cert}
        :param gke_cluster_endpoint: GKE cluster endpoint, i.e., cluster URI https://<DNS/IP>. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_endpoint TargetGke#gke_cluster_endpoint}
        :param gke_cluster_name: GKE cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_name TargetGke#gke_cluster_name}
        :param gke_service_account_email: GKE service account email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_service_account_email TargetGke#gke_service_account_email}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#id TargetGke#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#key TargetGke#key}
        :param use_gw_cloud_identity: Use the GW's Cloud IAM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#use_gw_cloud_identity TargetGke#use_gw_cloud_identity}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c0196b1a1100f86ceb2a038e9a56d06f1c956b2372f7e926ba98f2de03159da)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument gke_account_key", value=gke_account_key, expected_type=type_hints["gke_account_key"])
            check_type(argname="argument gke_cluster_cert", value=gke_cluster_cert, expected_type=type_hints["gke_cluster_cert"])
            check_type(argname="argument gke_cluster_endpoint", value=gke_cluster_endpoint, expected_type=type_hints["gke_cluster_endpoint"])
            check_type(argname="argument gke_cluster_name", value=gke_cluster_name, expected_type=type_hints["gke_cluster_name"])
            check_type(argname="argument gke_service_account_email", value=gke_service_account_email, expected_type=type_hints["gke_service_account_email"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument use_gw_cloud_identity", value=use_gw_cloud_identity, expected_type=type_hints["use_gw_cloud_identity"])
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
        if description is not None:
            self._values["description"] = description
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
        if key is not None:
            self._values["key"] = key
        if use_gw_cloud_identity is not None:
            self._values["use_gw_cloud_identity"] = use_gw_cloud_identity

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
        '''Target name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#name TargetGke#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#description TargetGke#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_account_key(self) -> typing.Optional[builtins.str]:
        '''GKE service account key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_account_key TargetGke#gke_account_key}
        '''
        result = self._values.get("gke_account_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_cluster_cert(self) -> typing.Optional[builtins.str]:
        '''GKE Base-64 encoded cluster certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_cert TargetGke#gke_cluster_cert}
        '''
        result = self._values.get("gke_cluster_cert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_cluster_endpoint(self) -> typing.Optional[builtins.str]:
        '''GKE cluster endpoint, i.e., cluster URI https://<DNS/IP>.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_endpoint TargetGke#gke_cluster_endpoint}
        '''
        result = self._values.get("gke_cluster_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_cluster_name(self) -> typing.Optional[builtins.str]:
        '''GKE cluster name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_cluster_name TargetGke#gke_cluster_name}
        '''
        result = self._values.get("gke_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gke_service_account_email(self) -> typing.Optional[builtins.str]:
        '''GKE service account email.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#gke_service_account_email TargetGke#gke_service_account_email}
        '''
        result = self._values.get("gke_service_account_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#id TargetGke#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#key TargetGke#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_gw_cloud_identity(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use the GW's Cloud IAM.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_gke#use_gw_cloud_identity TargetGke#use_gw_cloud_identity}
        '''
        result = self._values.get("use_gw_cloud_identity")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetGkeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TargetGke",
    "TargetGkeConfig",
]

publication.publish()

def _typecheckingstub__96c1a442b9cddecf1809691c9d4eb9c95761cbfe5c105ecb9ec173a78cd4538c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    gke_account_key: typing.Optional[builtins.str] = None,
    gke_cluster_cert: typing.Optional[builtins.str] = None,
    gke_cluster_endpoint: typing.Optional[builtins.str] = None,
    gke_cluster_name: typing.Optional[builtins.str] = None,
    gke_service_account_email: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    use_gw_cloud_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__14d65775338b1a94ee0ddf252dc06590af8b7a250b20593588e62d0d88f834ce(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0721d4b69945ea407bccac5633a2c2cdb9f24444f3855f3085a3236cd8c2ce40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8018cf3ce5204175b2d9e5ce65d4a66204f2c16dc1a7fe45cdb23a0918b47df7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45cafe2f47176ab07a2b54cf291a15d594140155a4f308c96f092b24fef81680(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e22208a803a30dd18d6bb8d4435db5e05f29475a142581ddf9032d4fd8197be5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b831df36ddb13d39c9deec0ea310840184d7a611b97d242f03106a6640a20a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19b87eb1cca6e85d680cba9192d211f94d555a45403cad52f6c59225a34b73f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df22c0430f1430bb56db5bab661047b70ae711e70bc017f40a74c1b214b6c8db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e8952475baa7ad880066ba741e455225bbd6b88fc196e9868b74749d9a0ea9f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fb296b3e2643a62c013b1afe9bb9562582109fe6e9435abe5bd18ae2675eadd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9be515bc468d28640e822a38bd5cf48b9aabccf8a4d893d69dc69e5de8f9ad7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c0196b1a1100f86ceb2a038e9a56d06f1c956b2372f7e926ba98f2de03159da(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    gke_account_key: typing.Optional[builtins.str] = None,
    gke_cluster_cert: typing.Optional[builtins.str] = None,
    gke_cluster_endpoint: typing.Optional[builtins.str] = None,
    gke_cluster_name: typing.Optional[builtins.str] = None,
    gke_service_account_email: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    use_gw_cloud_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
