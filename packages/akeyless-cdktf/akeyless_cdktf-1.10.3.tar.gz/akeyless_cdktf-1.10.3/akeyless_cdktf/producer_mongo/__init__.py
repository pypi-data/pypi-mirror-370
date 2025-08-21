'''
# `akeyless_producer_mongo`

Refer to the Terraform Registry for docs: [`akeyless_producer_mongo`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo).
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


class ProducerMongo(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerMongo.ProducerMongo",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo akeyless_producer_mongo}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
        mongodb_default_auth_db: typing.Optional[builtins.str] = None,
        mongodb_host_port: typing.Optional[builtins.str] = None,
        mongodb_name: typing.Optional[builtins.str] = None,
        mongodb_password: typing.Optional[builtins.str] = None,
        mongodb_roles: typing.Optional[builtins.str] = None,
        mongodb_server_uri: typing.Optional[builtins.str] = None,
        mongodb_uri_options: typing.Optional[builtins.str] = None,
        mongodb_username: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo akeyless_producer_mongo} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#name ProducerMongo#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#id ProducerMongo#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mongodb_atlas_api_private_key: MongoDB Atlas private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_api_private_key ProducerMongo#mongodb_atlas_api_private_key}
        :param mongodb_atlas_api_public_key: MongoDB Atlas public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_api_public_key ProducerMongo#mongodb_atlas_api_public_key}
        :param mongodb_atlas_project_id: MongoDB Atlas project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_project_id ProducerMongo#mongodb_atlas_project_id}
        :param mongodb_default_auth_db: MongoDB server default authentication database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_default_auth_db ProducerMongo#mongodb_default_auth_db}
        :param mongodb_host_port: host:port (e.g. my.mongo.db:27017). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_host_port ProducerMongo#mongodb_host_port}
        :param mongodb_name: MongoDB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_name ProducerMongo#mongodb_name}
        :param mongodb_password: MongoDB server password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_password ProducerMongo#mongodb_password}
        :param mongodb_roles: MongoDB roles (e.g. MongoDB:[{role:readWrite, db: sales}], MongoDB Atlas:[{roleName : readWrite, databaseName: sales}]). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_roles ProducerMongo#mongodb_roles}
        :param mongodb_server_uri: MongoDB server URI (e.g. mongodb://user:password@my.mongo.db:27017/admin?replicaSet=mySet). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_server_uri ProducerMongo#mongodb_server_uri}
        :param mongodb_uri_options: MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_uri_options ProducerMongo#mongodb_uri_options}
        :param mongodb_username: MongoDB server username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_username ProducerMongo#mongodb_username}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#producer_encryption_key_name ProducerMongo#producer_encryption_key_name}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_bastion_issuer ProducerMongo#secure_access_bastion_issuer}
        :param secure_access_db_name: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_db_name ProducerMongo#secure_access_db_name}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_enable ProducerMongo#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_host ProducerMongo#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_web ProducerMongo#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#tags ProducerMongo#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#target_name ProducerMongo#target_name}
        :param user_ttl: User TTL (e.g. 60s, 60m, 60h). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#user_ttl ProducerMongo#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82731b4ecee88c31e01b3da1ff99b1f201bb9cd2c18b6ed670467b1f0f1a1e29)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerMongoConfig(
            name=name,
            id=id,
            mongodb_atlas_api_private_key=mongodb_atlas_api_private_key,
            mongodb_atlas_api_public_key=mongodb_atlas_api_public_key,
            mongodb_atlas_project_id=mongodb_atlas_project_id,
            mongodb_default_auth_db=mongodb_default_auth_db,
            mongodb_host_port=mongodb_host_port,
            mongodb_name=mongodb_name,
            mongodb_password=mongodb_password,
            mongodb_roles=mongodb_roles,
            mongodb_server_uri=mongodb_server_uri,
            mongodb_uri_options=mongodb_uri_options,
            mongodb_username=mongodb_username,
            producer_encryption_key_name=producer_encryption_key_name,
            secure_access_bastion_issuer=secure_access_bastion_issuer,
            secure_access_db_name=secure_access_db_name,
            secure_access_enable=secure_access_enable,
            secure_access_host=secure_access_host,
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
        '''Generates CDKTF code for importing a ProducerMongo resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerMongo to import.
        :param import_from_id: The id of the existing ProducerMongo that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerMongo to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14597003b54630730b6198503b6291451d8443b4cddaaeb81d188dd086ba62c4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMongodbAtlasApiPrivateKey")
    def reset_mongodb_atlas_api_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbAtlasApiPrivateKey", []))

    @jsii.member(jsii_name="resetMongodbAtlasApiPublicKey")
    def reset_mongodb_atlas_api_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbAtlasApiPublicKey", []))

    @jsii.member(jsii_name="resetMongodbAtlasProjectId")
    def reset_mongodb_atlas_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbAtlasProjectId", []))

    @jsii.member(jsii_name="resetMongodbDefaultAuthDb")
    def reset_mongodb_default_auth_db(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbDefaultAuthDb", []))

    @jsii.member(jsii_name="resetMongodbHostPort")
    def reset_mongodb_host_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbHostPort", []))

    @jsii.member(jsii_name="resetMongodbName")
    def reset_mongodb_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbName", []))

    @jsii.member(jsii_name="resetMongodbPassword")
    def reset_mongodb_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbPassword", []))

    @jsii.member(jsii_name="resetMongodbRoles")
    def reset_mongodb_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbRoles", []))

    @jsii.member(jsii_name="resetMongodbServerUri")
    def reset_mongodb_server_uri(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbServerUri", []))

    @jsii.member(jsii_name="resetMongodbUriOptions")
    def reset_mongodb_uri_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbUriOptions", []))

    @jsii.member(jsii_name="resetMongodbUsername")
    def reset_mongodb_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongodbUsername", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

    @jsii.member(jsii_name="resetSecureAccessBastionIssuer")
    def reset_secure_access_bastion_issuer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessBastionIssuer", []))

    @jsii.member(jsii_name="resetSecureAccessDbName")
    def reset_secure_access_db_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessDbName", []))

    @jsii.member(jsii_name="resetSecureAccessEnable")
    def reset_secure_access_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessEnable", []))

    @jsii.member(jsii_name="resetSecureAccessHost")
    def reset_secure_access_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecureAccessHost", []))

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
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPrivateKeyInput")
    def mongodb_atlas_api_private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbAtlasApiPrivateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPublicKeyInput")
    def mongodb_atlas_api_public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbAtlasApiPublicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasProjectIdInput")
    def mongodb_atlas_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbAtlasProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbDefaultAuthDbInput")
    def mongodb_default_auth_db_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbDefaultAuthDbInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbHostPortInput")
    def mongodb_host_port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbHostPortInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbNameInput")
    def mongodb_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbNameInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbPasswordInput")
    def mongodb_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbRolesInput")
    def mongodb_roles_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbRolesInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbServerUriInput")
    def mongodb_server_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbServerUriInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbUriOptionsInput")
    def mongodb_uri_options_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbUriOptionsInput"))

    @builtins.property
    @jsii.member(jsii_name="mongodbUsernameInput")
    def mongodb_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongodbUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyNameInput")
    def producer_encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "producerEncryptionKeyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuerInput")
    def secure_access_bastion_issuer_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessBastionIssuerInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbNameInput")
    def secure_access_db_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessDbNameInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnableInput")
    def secure_access_enable_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secureAccessEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="secureAccessHostInput")
    def secure_access_host_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "secureAccessHostInput"))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab1149e875c916d12b2d8092f5adb3ec706ac27a25e17a2804990481bfac8a13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPrivateKey")
    def mongodb_atlas_api_private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasApiPrivateKey"))

    @mongodb_atlas_api_private_key.setter
    def mongodb_atlas_api_private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a46db18a2012ae9575f9e0c562ec937f268256f4e551191585d8f8f29f1111a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasApiPrivateKey", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPublicKey")
    def mongodb_atlas_api_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasApiPublicKey"))

    @mongodb_atlas_api_public_key.setter
    def mongodb_atlas_api_public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ec5cc0b01a999da733bccdd51f1665809f622f3161455e32b7940559acdb6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasApiPublicKey", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasProjectId")
    def mongodb_atlas_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasProjectId"))

    @mongodb_atlas_project_id.setter
    def mongodb_atlas_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__469419cd4d2d0b78210f9fd903031ea718884a71fc0b619c4adadf96c8b61cce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasProjectId", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbDefaultAuthDb")
    def mongodb_default_auth_db(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbDefaultAuthDb"))

    @mongodb_default_auth_db.setter
    def mongodb_default_auth_db(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebcdf1a4589056b76839fbb349e4677156131e8833454ae8ac977d40c159d329)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbDefaultAuthDb", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbHostPort")
    def mongodb_host_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbHostPort"))

    @mongodb_host_port.setter
    def mongodb_host_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9d317e2b15c29c1faf76cfdb1b243c0fb7211d389c0f2e19a19bb6739d5621e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbHostPort", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbName")
    def mongodb_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbName"))

    @mongodb_name.setter
    def mongodb_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18b25fb70afdbea2b9ca94ff32415ffcb81d7aa19883c15e4957bc33fed84e87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbName", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbPassword")
    def mongodb_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbPassword"))

    @mongodb_password.setter
    def mongodb_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__160197f655335444700fe7abee0610d6ad526c267a54a0468985fd19dff63ca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbPassword", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbRoles")
    def mongodb_roles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbRoles"))

    @mongodb_roles.setter
    def mongodb_roles(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d49e4146efa9857e9bfbc57479416e0563ccad9c72ac551b03deada1c8ba32b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbRoles", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbServerUri")
    def mongodb_server_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbServerUri"))

    @mongodb_server_uri.setter
    def mongodb_server_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f0914961f0fd736d29728a645c4811d43a6268ee1e1e1f47653114ac6add223)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbServerUri", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbUriOptions")
    def mongodb_uri_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbUriOptions"))

    @mongodb_uri_options.setter
    def mongodb_uri_options(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__526f4ddbfc934dce1aa3e7d47729437aca439effa11a378f5ceba89bcc79a91b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbUriOptions", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbUsername")
    def mongodb_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbUsername"))

    @mongodb_username.setter
    def mongodb_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f856a2fc193e19bfded73b986aeaeb0596c659a1b281b2e5a092d0bc7f5c44cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbUsername", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ce725e8c8a1ba05531b08212510d4a326cebba9fab21caf7437c0b21ce7268b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adf1a0615df06ec187016fdd68a189ded1cd75d19cc1ba91b0280c629fed5b46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59ffd87da939c025ce6e6787a53fcfefd61e7584f641bdaa93ddc0d750880cd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbName")
    def secure_access_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDbName"))

    @secure_access_db_name.setter
    def secure_access_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a9a8b13a45ffa4a1b757e11d91a256d82260c1f7bcfccbf752c393efc96da5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDbName", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65c2715f938aa81dac7b1b811b735bd8776831428fcad64b102bf374c45f9423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01d48266834acde0b4c613cb6178d203823c0c48741093cb38f843a58a238569)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessHost", value)

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
            type_hints = typing.get_type_hints(_typecheckingstub__f31e3d350e516bc441926fca216e8eccb963a06dc5cd02af2b25ec5b5a3828fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82dd5f7e1fb3f8de8d9107000bbd195740fb286dc976f038461dfea3ed16ef56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8c95d66720a399186607265c3c4ba7711025652aa96db696850f373a26a70a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f787e25094d7a2d17b614015eccc0fe3cb7edf46a9cb99646001251b09fcb08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerMongo.ProducerMongoConfig",
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
        "id": "id",
        "mongodb_atlas_api_private_key": "mongodbAtlasApiPrivateKey",
        "mongodb_atlas_api_public_key": "mongodbAtlasApiPublicKey",
        "mongodb_atlas_project_id": "mongodbAtlasProjectId",
        "mongodb_default_auth_db": "mongodbDefaultAuthDb",
        "mongodb_host_port": "mongodbHostPort",
        "mongodb_name": "mongodbName",
        "mongodb_password": "mongodbPassword",
        "mongodb_roles": "mongodbRoles",
        "mongodb_server_uri": "mongodbServerUri",
        "mongodb_uri_options": "mongodbUriOptions",
        "mongodb_username": "mongodbUsername",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "secure_access_bastion_issuer": "secureAccessBastionIssuer",
        "secure_access_db_name": "secureAccessDbName",
        "secure_access_enable": "secureAccessEnable",
        "secure_access_host": "secureAccessHost",
        "secure_access_web": "secureAccessWeb",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerMongoConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
        mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
        mongodb_default_auth_db: typing.Optional[builtins.str] = None,
        mongodb_host_port: typing.Optional[builtins.str] = None,
        mongodb_name: typing.Optional[builtins.str] = None,
        mongodb_password: typing.Optional[builtins.str] = None,
        mongodb_roles: typing.Optional[builtins.str] = None,
        mongodb_server_uri: typing.Optional[builtins.str] = None,
        mongodb_uri_options: typing.Optional[builtins.str] = None,
        mongodb_username: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
        secure_access_db_name: typing.Optional[builtins.str] = None,
        secure_access_enable: typing.Optional[builtins.str] = None,
        secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#name ProducerMongo#name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#id ProducerMongo#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mongodb_atlas_api_private_key: MongoDB Atlas private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_api_private_key ProducerMongo#mongodb_atlas_api_private_key}
        :param mongodb_atlas_api_public_key: MongoDB Atlas public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_api_public_key ProducerMongo#mongodb_atlas_api_public_key}
        :param mongodb_atlas_project_id: MongoDB Atlas project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_project_id ProducerMongo#mongodb_atlas_project_id}
        :param mongodb_default_auth_db: MongoDB server default authentication database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_default_auth_db ProducerMongo#mongodb_default_auth_db}
        :param mongodb_host_port: host:port (e.g. my.mongo.db:27017). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_host_port ProducerMongo#mongodb_host_port}
        :param mongodb_name: MongoDB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_name ProducerMongo#mongodb_name}
        :param mongodb_password: MongoDB server password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_password ProducerMongo#mongodb_password}
        :param mongodb_roles: MongoDB roles (e.g. MongoDB:[{role:readWrite, db: sales}], MongoDB Atlas:[{roleName : readWrite, databaseName: sales}]). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_roles ProducerMongo#mongodb_roles}
        :param mongodb_server_uri: MongoDB server URI (e.g. mongodb://user:password@my.mongo.db:27017/admin?replicaSet=mySet). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_server_uri ProducerMongo#mongodb_server_uri}
        :param mongodb_uri_options: MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_uri_options ProducerMongo#mongodb_uri_options}
        :param mongodb_username: MongoDB server username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_username ProducerMongo#mongodb_username}
        :param producer_encryption_key_name: Encrypt producer with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#producer_encryption_key_name ProducerMongo#producer_encryption_key_name}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_bastion_issuer ProducerMongo#secure_access_bastion_issuer}
        :param secure_access_db_name: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_db_name ProducerMongo#secure_access_db_name}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_enable ProducerMongo#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_host ProducerMongo#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_web ProducerMongo#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#tags ProducerMongo#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#target_name ProducerMongo#target_name}
        :param user_ttl: User TTL (e.g. 60s, 60m, 60h). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#user_ttl ProducerMongo#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb5bb90f8973c64fb80f7610865b3e3e7c1ca8ace8fac431dc463073f1920fd7)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument mongodb_atlas_api_private_key", value=mongodb_atlas_api_private_key, expected_type=type_hints["mongodb_atlas_api_private_key"])
            check_type(argname="argument mongodb_atlas_api_public_key", value=mongodb_atlas_api_public_key, expected_type=type_hints["mongodb_atlas_api_public_key"])
            check_type(argname="argument mongodb_atlas_project_id", value=mongodb_atlas_project_id, expected_type=type_hints["mongodb_atlas_project_id"])
            check_type(argname="argument mongodb_default_auth_db", value=mongodb_default_auth_db, expected_type=type_hints["mongodb_default_auth_db"])
            check_type(argname="argument mongodb_host_port", value=mongodb_host_port, expected_type=type_hints["mongodb_host_port"])
            check_type(argname="argument mongodb_name", value=mongodb_name, expected_type=type_hints["mongodb_name"])
            check_type(argname="argument mongodb_password", value=mongodb_password, expected_type=type_hints["mongodb_password"])
            check_type(argname="argument mongodb_roles", value=mongodb_roles, expected_type=type_hints["mongodb_roles"])
            check_type(argname="argument mongodb_server_uri", value=mongodb_server_uri, expected_type=type_hints["mongodb_server_uri"])
            check_type(argname="argument mongodb_uri_options", value=mongodb_uri_options, expected_type=type_hints["mongodb_uri_options"])
            check_type(argname="argument mongodb_username", value=mongodb_username, expected_type=type_hints["mongodb_username"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
            check_type(argname="argument secure_access_bastion_issuer", value=secure_access_bastion_issuer, expected_type=type_hints["secure_access_bastion_issuer"])
            check_type(argname="argument secure_access_db_name", value=secure_access_db_name, expected_type=type_hints["secure_access_db_name"])
            check_type(argname="argument secure_access_enable", value=secure_access_enable, expected_type=type_hints["secure_access_enable"])
            check_type(argname="argument secure_access_host", value=secure_access_host, expected_type=type_hints["secure_access_host"])
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
        if id is not None:
            self._values["id"] = id
        if mongodb_atlas_api_private_key is not None:
            self._values["mongodb_atlas_api_private_key"] = mongodb_atlas_api_private_key
        if mongodb_atlas_api_public_key is not None:
            self._values["mongodb_atlas_api_public_key"] = mongodb_atlas_api_public_key
        if mongodb_atlas_project_id is not None:
            self._values["mongodb_atlas_project_id"] = mongodb_atlas_project_id
        if mongodb_default_auth_db is not None:
            self._values["mongodb_default_auth_db"] = mongodb_default_auth_db
        if mongodb_host_port is not None:
            self._values["mongodb_host_port"] = mongodb_host_port
        if mongodb_name is not None:
            self._values["mongodb_name"] = mongodb_name
        if mongodb_password is not None:
            self._values["mongodb_password"] = mongodb_password
        if mongodb_roles is not None:
            self._values["mongodb_roles"] = mongodb_roles
        if mongodb_server_uri is not None:
            self._values["mongodb_server_uri"] = mongodb_server_uri
        if mongodb_uri_options is not None:
            self._values["mongodb_uri_options"] = mongodb_uri_options
        if mongodb_username is not None:
            self._values["mongodb_username"] = mongodb_username
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
        if secure_access_bastion_issuer is not None:
            self._values["secure_access_bastion_issuer"] = secure_access_bastion_issuer
        if secure_access_db_name is not None:
            self._values["secure_access_db_name"] = secure_access_db_name
        if secure_access_enable is not None:
            self._values["secure_access_enable"] = secure_access_enable
        if secure_access_host is not None:
            self._values["secure_access_host"] = secure_access_host
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#name ProducerMongo#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#id ProducerMongo#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_api_private_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas private key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_api_private_key ProducerMongo#mongodb_atlas_api_private_key}
        '''
        result = self._values.get("mongodb_atlas_api_private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_api_public_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas public key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_api_public_key ProducerMongo#mongodb_atlas_api_public_key}
        '''
        result = self._values.get("mongodb_atlas_api_public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_project_id(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas project ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_atlas_project_id ProducerMongo#mongodb_atlas_project_id}
        '''
        result = self._values.get("mongodb_atlas_project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_default_auth_db(self) -> typing.Optional[builtins.str]:
        '''MongoDB server default authentication database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_default_auth_db ProducerMongo#mongodb_default_auth_db}
        '''
        result = self._values.get("mongodb_default_auth_db")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_host_port(self) -> typing.Optional[builtins.str]:
        '''host:port (e.g. my.mongo.db:27017).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_host_port ProducerMongo#mongodb_host_port}
        '''
        result = self._values.get("mongodb_host_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_name(self) -> typing.Optional[builtins.str]:
        '''MongoDB name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_name ProducerMongo#mongodb_name}
        '''
        result = self._values.get("mongodb_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_password(self) -> typing.Optional[builtins.str]:
        '''MongoDB server password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_password ProducerMongo#mongodb_password}
        '''
        result = self._values.get("mongodb_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_roles(self) -> typing.Optional[builtins.str]:
        '''MongoDB roles (e.g. MongoDB:[{role:readWrite, db: sales}], MongoDB Atlas:[{roleName : readWrite, databaseName: sales}]).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_roles ProducerMongo#mongodb_roles}
        '''
        result = self._values.get("mongodb_roles")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_server_uri(self) -> typing.Optional[builtins.str]:
        '''MongoDB server URI (e.g. mongodb://user:password@my.mongo.db:27017/admin?replicaSet=mySet).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_server_uri ProducerMongo#mongodb_server_uri}
        '''
        result = self._values.get("mongodb_server_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_uri_options(self) -> typing.Optional[builtins.str]:
        '''MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_uri_options ProducerMongo#mongodb_uri_options}
        '''
        result = self._values.get("mongodb_uri_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_username(self) -> typing.Optional[builtins.str]:
        '''MongoDB server username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#mongodb_username ProducerMongo#mongodb_username}
        '''
        result = self._values.get("mongodb_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt producer with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#producer_encryption_key_name ProducerMongo#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_bastion_issuer ProducerMongo#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_db_name(self) -> typing.Optional[builtins.str]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_db_name ProducerMongo#secure_access_db_name}
        '''
        result = self._values.get("secure_access_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_enable ProducerMongo#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target DB servers for connections., For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_host ProducerMongo#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#secure_access_web ProducerMongo#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#tags ProducerMongo#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#target_name ProducerMongo#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL (e.g. 60s, 60m, 60h).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_mongo#user_ttl ProducerMongo#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerMongoConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerMongo",
    "ProducerMongoConfig",
]

publication.publish()

def _typecheckingstub__82731b4ecee88c31e01b3da1ff99b1f201bb9cd2c18b6ed670467b1f0f1a1e29(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
    mongodb_default_auth_db: typing.Optional[builtins.str] = None,
    mongodb_host_port: typing.Optional[builtins.str] = None,
    mongodb_name: typing.Optional[builtins.str] = None,
    mongodb_password: typing.Optional[builtins.str] = None,
    mongodb_roles: typing.Optional[builtins.str] = None,
    mongodb_server_uri: typing.Optional[builtins.str] = None,
    mongodb_uri_options: typing.Optional[builtins.str] = None,
    mongodb_username: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__14597003b54630730b6198503b6291451d8443b4cddaaeb81d188dd086ba62c4(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab1149e875c916d12b2d8092f5adb3ec706ac27a25e17a2804990481bfac8a13(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a46db18a2012ae9575f9e0c562ec937f268256f4e551191585d8f8f29f1111a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ec5cc0b01a999da733bccdd51f1665809f622f3161455e32b7940559acdb6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__469419cd4d2d0b78210f9fd903031ea718884a71fc0b619c4adadf96c8b61cce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebcdf1a4589056b76839fbb349e4677156131e8833454ae8ac977d40c159d329(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9d317e2b15c29c1faf76cfdb1b243c0fb7211d389c0f2e19a19bb6739d5621e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18b25fb70afdbea2b9ca94ff32415ffcb81d7aa19883c15e4957bc33fed84e87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__160197f655335444700fe7abee0610d6ad526c267a54a0468985fd19dff63ca4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d49e4146efa9857e9bfbc57479416e0563ccad9c72ac551b03deada1c8ba32b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f0914961f0fd736d29728a645c4811d43a6268ee1e1e1f47653114ac6add223(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__526f4ddbfc934dce1aa3e7d47729437aca439effa11a378f5ceba89bcc79a91b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f856a2fc193e19bfded73b986aeaeb0596c659a1b281b2e5a092d0bc7f5c44cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ce725e8c8a1ba05531b08212510d4a326cebba9fab21caf7437c0b21ce7268b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adf1a0615df06ec187016fdd68a189ded1cd75d19cc1ba91b0280c629fed5b46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59ffd87da939c025ce6e6787a53fcfefd61e7584f641bdaa93ddc0d750880cd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a9a8b13a45ffa4a1b757e11d91a256d82260c1f7bcfccbf752c393efc96da5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65c2715f938aa81dac7b1b811b735bd8776831428fcad64b102bf374c45f9423(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01d48266834acde0b4c613cb6178d203823c0c48741093cb38f843a58a238569(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f31e3d350e516bc441926fca216e8eccb963a06dc5cd02af2b25ec5b5a3828fc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82dd5f7e1fb3f8de8d9107000bbd195740fb286dc976f038461dfea3ed16ef56(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8c95d66720a399186607265c3c4ba7711025652aa96db696850f373a26a70a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f787e25094d7a2d17b614015eccc0fe3cb7edf46a9cb99646001251b09fcb08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb5bb90f8973c64fb80f7610865b3e3e7c1ca8ace8fac431dc463073f1920fd7(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    id: typing.Optional[builtins.str] = None,
    mongodb_atlas_api_private_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_api_public_key: typing.Optional[builtins.str] = None,
    mongodb_atlas_project_id: typing.Optional[builtins.str] = None,
    mongodb_default_auth_db: typing.Optional[builtins.str] = None,
    mongodb_host_port: typing.Optional[builtins.str] = None,
    mongodb_name: typing.Optional[builtins.str] = None,
    mongodb_password: typing.Optional[builtins.str] = None,
    mongodb_roles: typing.Optional[builtins.str] = None,
    mongodb_server_uri: typing.Optional[builtins.str] = None,
    mongodb_uri_options: typing.Optional[builtins.str] = None,
    mongodb_username: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    secure_access_bastion_issuer: typing.Optional[builtins.str] = None,
    secure_access_db_name: typing.Optional[builtins.str] = None,
    secure_access_enable: typing.Optional[builtins.str] = None,
    secure_access_host: typing.Optional[typing.Sequence[builtins.str]] = None,
    secure_access_web: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
