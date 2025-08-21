'''
# `akeyless_target_eks`

Refer to the Terraform Registry for docs: [`akeyless_target_eks`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks).
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


class TargetEks(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.targetEks.TargetEks",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks akeyless_target_eks}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        eks_access_key_id: builtins.str,
        eks_cluster_ca_cert: builtins.str,
        eks_cluster_endpoint: builtins.str,
        eks_cluster_name: builtins.str,
        eks_secret_access_key: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        eks_region: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks akeyless_target_eks} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param eks_access_key_id: EKS access key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_access_key_id TargetEks#eks_access_key_id}
        :param eks_cluster_ca_cert: EKS cluster base-64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_ca_cert TargetEks#eks_cluster_ca_cert}
        :param eks_cluster_endpoint: EKS cluster endpoint (i.e., https:// of the cluster). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_endpoint TargetEks#eks_cluster_endpoint}
        :param eks_cluster_name: EKS cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_name TargetEks#eks_cluster_name}
        :param eks_secret_access_key: EKS secret access key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_secret_access_key TargetEks#eks_secret_access_key}
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#name TargetEks#name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#description TargetEks#description}
        :param eks_region: EKS region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_region TargetEks#eks_region}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#id TargetEks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#key TargetEks#key}
        :param use_gw_cloud_identity: Use the GW's Cloud IAM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#use_gw_cloud_identity TargetEks#use_gw_cloud_identity}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5468002f85ddd98d445213374129ab55af6f0b15b80a9f58db6f6e0553d95c7b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TargetEksConfig(
            eks_access_key_id=eks_access_key_id,
            eks_cluster_ca_cert=eks_cluster_ca_cert,
            eks_cluster_endpoint=eks_cluster_endpoint,
            eks_cluster_name=eks_cluster_name,
            eks_secret_access_key=eks_secret_access_key,
            name=name,
            description=description,
            eks_region=eks_region,
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
        '''Generates CDKTF code for importing a TargetEks resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the TargetEks to import.
        :param import_from_id: The id of the existing TargetEks that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the TargetEks to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ca78259a05f6fdf226983ed38883541c3dd645dd79330717bdc1ec9e99ed135)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEksRegion")
    def reset_eks_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEksRegion", []))

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
    @jsii.member(jsii_name="eksAccessKeyIdInput")
    def eks_access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eksAccessKeyIdInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2bca2fadd6eaaf6aa1f62bc2ed7bd67b2d8d73d501a3327c292812f26b91bf07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="eksAccessKeyId")
    def eks_access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksAccessKeyId"))

    @eks_access_key_id.setter
    def eks_access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b47a96ed48a2dde0ed48f81178610578d09baf85219425f71b62246c2bbb304a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksAccessKeyId", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterCaCert")
    def eks_cluster_ca_cert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterCaCert"))

    @eks_cluster_ca_cert.setter
    def eks_cluster_ca_cert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8714797310c3d0c9e4eb7bd4724c8bf7f354af6b68db307036b0958e0b778a3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterCaCert", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterEndpoint")
    def eks_cluster_endpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterEndpoint"))

    @eks_cluster_endpoint.setter
    def eks_cluster_endpoint(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__295e075513b243e6f9bb7a7712a1d5a219dc6dd69ee99468e14b2bd5bb97af6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterEndpoint", value)

    @builtins.property
    @jsii.member(jsii_name="eksClusterName")
    def eks_cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksClusterName"))

    @eks_cluster_name.setter
    def eks_cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24760835cece1f7d2b8d94d2d710353e531d00ed201939c71511ed935c3cf327)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksClusterName", value)

    @builtins.property
    @jsii.member(jsii_name="eksRegion")
    def eks_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksRegion"))

    @eks_region.setter
    def eks_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9fd9aa23c69fa84296c284e2d335c27bc32a9982813e3f433df93d1ad205287)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksRegion", value)

    @builtins.property
    @jsii.member(jsii_name="eksSecretAccessKey")
    def eks_secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eksSecretAccessKey"))

    @eks_secret_access_key.setter
    def eks_secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6135fb80cecb7cfd13576f4947b906b3d828a0eacf077e324b9dbf38d55472c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eksSecretAccessKey", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40eff38a0173559eed0212c0c6a8a36893eda39b13ea266912c570dd5cd7d9f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55ed9fa21692e7939650943050db39d13f2dda697b2c2fcc5e0b912353d57f41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f1a284e87966b64363175d2dee6231b2d0ff98e9bc5553cef011c75f7a1bb1f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__956ab9ea1b0200eda98bd5a18878eadda5aaa96068aaf7f0b5a31ad4b94a49c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useGwCloudIdentity", value)


@jsii.data_type(
    jsii_type="akeyless.targetEks.TargetEksConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "eks_access_key_id": "eksAccessKeyId",
        "eks_cluster_ca_cert": "eksClusterCaCert",
        "eks_cluster_endpoint": "eksClusterEndpoint",
        "eks_cluster_name": "eksClusterName",
        "eks_secret_access_key": "eksSecretAccessKey",
        "name": "name",
        "description": "description",
        "eks_region": "eksRegion",
        "id": "id",
        "key": "key",
        "use_gw_cloud_identity": "useGwCloudIdentity",
    },
)
class TargetEksConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        eks_access_key_id: builtins.str,
        eks_cluster_ca_cert: builtins.str,
        eks_cluster_endpoint: builtins.str,
        eks_cluster_name: builtins.str,
        eks_secret_access_key: builtins.str,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        eks_region: typing.Optional[builtins.str] = None,
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
        :param eks_access_key_id: EKS access key ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_access_key_id TargetEks#eks_access_key_id}
        :param eks_cluster_ca_cert: EKS cluster base-64 encoded certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_ca_cert TargetEks#eks_cluster_ca_cert}
        :param eks_cluster_endpoint: EKS cluster endpoint (i.e., https:// of the cluster). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_endpoint TargetEks#eks_cluster_endpoint}
        :param eks_cluster_name: EKS cluster name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_name TargetEks#eks_cluster_name}
        :param eks_secret_access_key: EKS secret access key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_secret_access_key TargetEks#eks_secret_access_key}
        :param name: Target name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#name TargetEks#name}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#description TargetEks#description}
        :param eks_region: EKS region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_region TargetEks#eks_region}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#id TargetEks#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key: Key name. The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#key TargetEks#key}
        :param use_gw_cloud_identity: Use the GW's Cloud IAM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#use_gw_cloud_identity TargetEks#use_gw_cloud_identity}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19d25a86946f8a062357a9224c4081605bc2a2666ae2cc862aae0591a52444aa)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument eks_access_key_id", value=eks_access_key_id, expected_type=type_hints["eks_access_key_id"])
            check_type(argname="argument eks_cluster_ca_cert", value=eks_cluster_ca_cert, expected_type=type_hints["eks_cluster_ca_cert"])
            check_type(argname="argument eks_cluster_endpoint", value=eks_cluster_endpoint, expected_type=type_hints["eks_cluster_endpoint"])
            check_type(argname="argument eks_cluster_name", value=eks_cluster_name, expected_type=type_hints["eks_cluster_name"])
            check_type(argname="argument eks_secret_access_key", value=eks_secret_access_key, expected_type=type_hints["eks_secret_access_key"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument eks_region", value=eks_region, expected_type=type_hints["eks_region"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument use_gw_cloud_identity", value=use_gw_cloud_identity, expected_type=type_hints["use_gw_cloud_identity"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "eks_access_key_id": eks_access_key_id,
            "eks_cluster_ca_cert": eks_cluster_ca_cert,
            "eks_cluster_endpoint": eks_cluster_endpoint,
            "eks_cluster_name": eks_cluster_name,
            "eks_secret_access_key": eks_secret_access_key,
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
        if eks_region is not None:
            self._values["eks_region"] = eks_region
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
    def eks_access_key_id(self) -> builtins.str:
        '''EKS access key ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_access_key_id TargetEks#eks_access_key_id}
        '''
        result = self._values.get("eks_access_key_id")
        assert result is not None, "Required property 'eks_access_key_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eks_cluster_ca_cert(self) -> builtins.str:
        '''EKS cluster base-64 encoded certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_ca_cert TargetEks#eks_cluster_ca_cert}
        '''
        result = self._values.get("eks_cluster_ca_cert")
        assert result is not None, "Required property 'eks_cluster_ca_cert' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eks_cluster_endpoint(self) -> builtins.str:
        '''EKS cluster endpoint (i.e., https:// of the cluster).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_endpoint TargetEks#eks_cluster_endpoint}
        '''
        result = self._values.get("eks_cluster_endpoint")
        assert result is not None, "Required property 'eks_cluster_endpoint' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eks_cluster_name(self) -> builtins.str:
        '''EKS cluster name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_cluster_name TargetEks#eks_cluster_name}
        '''
        result = self._values.get("eks_cluster_name")
        assert result is not None, "Required property 'eks_cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def eks_secret_access_key(self) -> builtins.str:
        '''EKS secret access key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_secret_access_key TargetEks#eks_secret_access_key}
        '''
        result = self._values.get("eks_secret_access_key")
        assert result is not None, "Required property 'eks_secret_access_key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Target name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#name TargetEks#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#description TargetEks#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def eks_region(self) -> typing.Optional[builtins.str]:
        '''EKS region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#eks_region TargetEks#eks_region}
        '''
        result = self._values.get("eks_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#id TargetEks#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Key name.

        The key will be used to encrypt the target secret value. If key name is not specified, the account default protection key is used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#key TargetEks#key}
        '''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def use_gw_cloud_identity(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Use the GW's Cloud IAM.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/target_eks#use_gw_cloud_identity TargetEks#use_gw_cloud_identity}
        '''
        result = self._values.get("use_gw_cloud_identity")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TargetEksConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "TargetEks",
    "TargetEksConfig",
]

publication.publish()

def _typecheckingstub__5468002f85ddd98d445213374129ab55af6f0b15b80a9f58db6f6e0553d95c7b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    eks_access_key_id: builtins.str,
    eks_cluster_ca_cert: builtins.str,
    eks_cluster_endpoint: builtins.str,
    eks_cluster_name: builtins.str,
    eks_secret_access_key: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    eks_region: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6ca78259a05f6fdf226983ed38883541c3dd645dd79330717bdc1ec9e99ed135(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bca2fadd6eaaf6aa1f62bc2ed7bd67b2d8d73d501a3327c292812f26b91bf07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b47a96ed48a2dde0ed48f81178610578d09baf85219425f71b62246c2bbb304a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8714797310c3d0c9e4eb7bd4724c8bf7f354af6b68db307036b0958e0b778a3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__295e075513b243e6f9bb7a7712a1d5a219dc6dd69ee99468e14b2bd5bb97af6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24760835cece1f7d2b8d94d2d710353e531d00ed201939c71511ed935c3cf327(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9fd9aa23c69fa84296c284e2d335c27bc32a9982813e3f433df93d1ad205287(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6135fb80cecb7cfd13576f4947b906b3d828a0eacf077e324b9dbf38d55472c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40eff38a0173559eed0212c0c6a8a36893eda39b13ea266912c570dd5cd7d9f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55ed9fa21692e7939650943050db39d13f2dda697b2c2fcc5e0b912353d57f41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f1a284e87966b64363175d2dee6231b2d0ff98e9bc5553cef011c75f7a1bb1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__956ab9ea1b0200eda98bd5a18878eadda5aaa96068aaf7f0b5a31ad4b94a49c2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19d25a86946f8a062357a9224c4081605bc2a2666ae2cc862aae0591a52444aa(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    eks_access_key_id: builtins.str,
    eks_cluster_ca_cert: builtins.str,
    eks_cluster_endpoint: builtins.str,
    eks_cluster_name: builtins.str,
    eks_secret_access_key: builtins.str,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    eks_region: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    key: typing.Optional[builtins.str] = None,
    use_gw_cloud_identity: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass
