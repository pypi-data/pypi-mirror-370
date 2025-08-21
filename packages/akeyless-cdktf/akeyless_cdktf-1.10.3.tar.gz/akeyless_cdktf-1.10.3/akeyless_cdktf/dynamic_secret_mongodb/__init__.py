'''
# `akeyless_dynamic_secret_mongodb`

Refer to the Terraform Registry for docs: [`akeyless_dynamic_secret_mongodb`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb).
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


class DynamicSecretMongodb(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.dynamicSecretMongodb.DynamicSecretMongodb",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb akeyless_dynamic_secret_mongodb}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        custom_username_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
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
        password_length: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb akeyless_dynamic_secret_mongodb} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#name DynamicSecretMongodb#name}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#custom_username_template DynamicSecretMongodb#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#encryption_key_name DynamicSecretMongodb#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#id DynamicSecretMongodb#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mongodb_atlas_api_private_key: MongoDB Atlas private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_api_private_key DynamicSecretMongodb#mongodb_atlas_api_private_key}
        :param mongodb_atlas_api_public_key: MongoDB Atlas public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_api_public_key DynamicSecretMongodb#mongodb_atlas_api_public_key}
        :param mongodb_atlas_project_id: MongoDB Atlas project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_project_id DynamicSecretMongodb#mongodb_atlas_project_id}
        :param mongodb_default_auth_db: MongoDB server default authentication database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_default_auth_db DynamicSecretMongodb#mongodb_default_auth_db}
        :param mongodb_host_port: host:port (e.g. my.mongo.db:27017). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_host_port DynamicSecretMongodb#mongodb_host_port}
        :param mongodb_name: MongoDB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_name DynamicSecretMongodb#mongodb_name}
        :param mongodb_password: MongoDB server password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_password DynamicSecretMongodb#mongodb_password}
        :param mongodb_roles: MongoDB roles (e.g. MongoDB:[{role:readWrite, db: sales}], MongoDB Atlas:[{roleName : readWrite, databaseName: sales}]). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_roles DynamicSecretMongodb#mongodb_roles}
        :param mongodb_server_uri: MongoDB server URI (e.g. mongodb://user:password@my.mongo.db:27017/admin?replicaSet=mySet). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_server_uri DynamicSecretMongodb#mongodb_server_uri}
        :param mongodb_uri_options: MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_uri_options DynamicSecretMongodb#mongodb_uri_options}
        :param mongodb_username: MongoDB server username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_username DynamicSecretMongodb#mongodb_username}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#password_length DynamicSecretMongodb#password_length}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_bastion_issuer DynamicSecretMongodb#secure_access_bastion_issuer}
        :param secure_access_db_name: The DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_db_name DynamicSecretMongodb#secure_access_db_name}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_enable DynamicSecretMongodb#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_host DynamicSecretMongodb#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_web DynamicSecretMongodb#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#tags DynamicSecretMongodb#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#target_name DynamicSecretMongodb#target_name}
        :param user_ttl: User TTL (e.g. 60s, 60m, 60h). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#user_ttl DynamicSecretMongodb#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__846bf15c981dfa6246806cd102ae7a73629f2d4449e79650821e3802af3eccd9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DynamicSecretMongodbConfig(
            name=name,
            custom_username_template=custom_username_template,
            encryption_key_name=encryption_key_name,
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
            password_length=password_length,
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
        '''Generates CDKTF code for importing a DynamicSecretMongodb resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DynamicSecretMongodb to import.
        :param import_from_id: The id of the existing DynamicSecretMongodb that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DynamicSecretMongodb to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a64881ca4f819fed446dfc27402fca747d2aed9f869ab13fb7bc6b394f14ac2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetCustomUsernameTemplate")
    def reset_custom_username_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomUsernameTemplate", []))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

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

    @jsii.member(jsii_name="resetPasswordLength")
    def reset_password_length(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPasswordLength", []))

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
    @jsii.member(jsii_name="customUsernameTemplateInput")
    def custom_username_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customUsernameTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyNameInput")
    def encryption_key_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKeyNameInput"))

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
    @jsii.member(jsii_name="passwordLengthInput")
    def password_length_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordLengthInput"))

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
    @jsii.member(jsii_name="customUsernameTemplate")
    def custom_username_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customUsernameTemplate"))

    @custom_username_template.setter
    def custom_username_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c79da567694f9445546ec680ef52a33956417c2dfebf007aac342e24ce6385bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customUsernameTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc46ae4eada89dbf1cc5efd664879fd066c239e3f0d778210475dced46ec66e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5eab8054584b7e0fcfe8fc2b12bd48593c36935291488e7b5fdc7570765b830e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPrivateKey")
    def mongodb_atlas_api_private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasApiPrivateKey"))

    @mongodb_atlas_api_private_key.setter
    def mongodb_atlas_api_private_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5070e77eb322e1695fa09dd78da55721686f1c5166f8ac9c825b13dccf84892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasApiPrivateKey", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasApiPublicKey")
    def mongodb_atlas_api_public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasApiPublicKey"))

    @mongodb_atlas_api_public_key.setter
    def mongodb_atlas_api_public_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f53ad833fbb147c0a5b94e6baabfe3d73b8c9962dec3a5f5d4a233d2417a979f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasApiPublicKey", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbAtlasProjectId")
    def mongodb_atlas_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbAtlasProjectId"))

    @mongodb_atlas_project_id.setter
    def mongodb_atlas_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c895a09950c33623d0d2d189f82f3a8f2143e6594c95e152bba1c61457877f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbAtlasProjectId", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbDefaultAuthDb")
    def mongodb_default_auth_db(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbDefaultAuthDb"))

    @mongodb_default_auth_db.setter
    def mongodb_default_auth_db(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8da568b4cfe20630c5fd5c03fa65a9361e382c7ed4293cf3956da5e2584a90d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbDefaultAuthDb", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbHostPort")
    def mongodb_host_port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbHostPort"))

    @mongodb_host_port.setter
    def mongodb_host_port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cad6f83ff06743d65f1dbc4960266aa5b8b710c216714f57fbdc8a5bd8482a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbHostPort", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbName")
    def mongodb_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbName"))

    @mongodb_name.setter
    def mongodb_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20109c4a5799c54183b2e47d57f7079d1207d14aad3ffe5400c729e166891d87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbName", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbPassword")
    def mongodb_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbPassword"))

    @mongodb_password.setter
    def mongodb_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c06d858165ccc0ff9cd053f2444ce975c154d8e80ca76e7cd4410f42bcd5d28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbPassword", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbRoles")
    def mongodb_roles(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbRoles"))

    @mongodb_roles.setter
    def mongodb_roles(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51a5f6aefee851ee021ee76daeb1422c11ad7caebff8b92c6ca7a71415093d02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbRoles", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbServerUri")
    def mongodb_server_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbServerUri"))

    @mongodb_server_uri.setter
    def mongodb_server_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab49a0867cc73b7e1aa4533deebe243e7233893fe082d1935a2047c0090caf92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbServerUri", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbUriOptions")
    def mongodb_uri_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbUriOptions"))

    @mongodb_uri_options.setter
    def mongodb_uri_options(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3101b5600d36be2dc05fa3ca85e17bbcf8444020f9f77e311b700951702788a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbUriOptions", value)

    @builtins.property
    @jsii.member(jsii_name="mongodbUsername")
    def mongodb_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongodbUsername"))

    @mongodb_username.setter
    def mongodb_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e48e6340608df6a7c39c675503bb03103e187f930819e616aa60fcd26a05209)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongodbUsername", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16c4034ac1d38db82c19cb3db258b6f0b27b57ae8bd273d5130ed449aff067d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="passwordLength")
    def password_length(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "passwordLength"))

    @password_length.setter
    def password_length(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__590a9ac709acc22fc0621af631e28654c0a0d201cfdf966ebd05a76efcc41c8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "passwordLength", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessBastionIssuer")
    def secure_access_bastion_issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessBastionIssuer"))

    @secure_access_bastion_issuer.setter
    def secure_access_bastion_issuer(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c577949cf77e5036c7da8ff1bc15c31e3fdd5c51f9c1a593e751ad73137280e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessBastionIssuer", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessDbName")
    def secure_access_db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessDbName"))

    @secure_access_db_name.setter
    def secure_access_db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5bcb7231039944616ac7aa0e2b47b1614282a57bddde6c3365e73cc84290e46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessDbName", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessEnable")
    def secure_access_enable(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secureAccessEnable"))

    @secure_access_enable.setter
    def secure_access_enable(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b72055ad9e1180be326ac7ec197dbf5c85765cddf5fcd97e5d6d8bdcf434a121)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessEnable", value)

    @builtins.property
    @jsii.member(jsii_name="secureAccessHost")
    def secure_access_host(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "secureAccessHost"))

    @secure_access_host.setter
    def secure_access_host(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b29505a9340bc97cd04d8e63d3e7643f515a0efa858dec0590e342fba7857f8d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba909b192bbe164e3e72729a6c75264412fafecf7e23c60cba83e8bdd2d7a473)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secureAccessWeb", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e28c588031f31d76e4871b008d4cfdf8715b9c858222286f31ff9d5701cc8f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73f21a0c8ab4e9f75efef071501a4f150686c38498adf77b41ea5943be459f3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0e9dfd0105f99f5b9a0ec13f427604d3d57df3571b14760a38e5fd050e80877)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.dynamicSecretMongodb.DynamicSecretMongodbConfig",
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
        "encryption_key_name": "encryptionKeyName",
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
        "password_length": "passwordLength",
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
class DynamicSecretMongodbConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        encryption_key_name: typing.Optional[builtins.str] = None,
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
        password_length: typing.Optional[builtins.str] = None,
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
        :param name: Dynamic secret name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#name DynamicSecretMongodb#name}
        :param custom_username_template: Customize how temporary usernames are generated using go template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#custom_username_template DynamicSecretMongodb#custom_username_template}
        :param encryption_key_name: Encrypt dynamic secret details with following key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#encryption_key_name DynamicSecretMongodb#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#id DynamicSecretMongodb#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param mongodb_atlas_api_private_key: MongoDB Atlas private key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_api_private_key DynamicSecretMongodb#mongodb_atlas_api_private_key}
        :param mongodb_atlas_api_public_key: MongoDB Atlas public key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_api_public_key DynamicSecretMongodb#mongodb_atlas_api_public_key}
        :param mongodb_atlas_project_id: MongoDB Atlas project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_project_id DynamicSecretMongodb#mongodb_atlas_project_id}
        :param mongodb_default_auth_db: MongoDB server default authentication database. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_default_auth_db DynamicSecretMongodb#mongodb_default_auth_db}
        :param mongodb_host_port: host:port (e.g. my.mongo.db:27017). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_host_port DynamicSecretMongodb#mongodb_host_port}
        :param mongodb_name: MongoDB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_name DynamicSecretMongodb#mongodb_name}
        :param mongodb_password: MongoDB server password. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_password DynamicSecretMongodb#mongodb_password}
        :param mongodb_roles: MongoDB roles (e.g. MongoDB:[{role:readWrite, db: sales}], MongoDB Atlas:[{roleName : readWrite, databaseName: sales}]). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_roles DynamicSecretMongodb#mongodb_roles}
        :param mongodb_server_uri: MongoDB server URI (e.g. mongodb://user:password@my.mongo.db:27017/admin?replicaSet=mySet). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_server_uri DynamicSecretMongodb#mongodb_server_uri}
        :param mongodb_uri_options: MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_uri_options DynamicSecretMongodb#mongodb_uri_options}
        :param mongodb_username: MongoDB server username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_username DynamicSecretMongodb#mongodb_username}
        :param password_length: The length of the password to be generated. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#password_length DynamicSecretMongodb#password_length}
        :param secure_access_bastion_issuer: Path to the SSH Certificate Issuer for your Akeyless Bastion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_bastion_issuer DynamicSecretMongodb#secure_access_bastion_issuer}
        :param secure_access_db_name: The DB name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_db_name DynamicSecretMongodb#secure_access_db_name}
        :param secure_access_enable: Enable/Disable secure remote access, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_enable DynamicSecretMongodb#secure_access_enable}
        :param secure_access_host: Target DB servers for connections., For multiple values repeat this flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_host DynamicSecretMongodb#secure_access_host}
        :param secure_access_web: Enable Web Secure Remote Access. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_web DynamicSecretMongodb#secure_access_web}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: -t Tag1 -t Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#tags DynamicSecretMongodb#tags}
        :param target_name: Name of existing target to use in dynamic secret creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#target_name DynamicSecretMongodb#target_name}
        :param user_ttl: User TTL (e.g. 60s, 60m, 60h). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#user_ttl DynamicSecretMongodb#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18a5ed1ef326ec173fd4e520d1a4484694b0a60a6b0af55f758a857d44e2a529)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument custom_username_template", value=custom_username_template, expected_type=type_hints["custom_username_template"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
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
            check_type(argname="argument password_length", value=password_length, expected_type=type_hints["password_length"])
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
        if custom_username_template is not None:
            self._values["custom_username_template"] = custom_username_template
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
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
        if password_length is not None:
            self._values["password_length"] = password_length
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
        '''Dynamic secret name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#name DynamicSecretMongodb#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def custom_username_template(self) -> typing.Optional[builtins.str]:
        '''Customize how temporary usernames are generated using go template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#custom_username_template DynamicSecretMongodb#custom_username_template}
        '''
        result = self._values.get("custom_username_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Encrypt dynamic secret details with following key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#encryption_key_name DynamicSecretMongodb#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#id DynamicSecretMongodb#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_api_private_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas private key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_api_private_key DynamicSecretMongodb#mongodb_atlas_api_private_key}
        '''
        result = self._values.get("mongodb_atlas_api_private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_api_public_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas public key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_api_public_key DynamicSecretMongodb#mongodb_atlas_api_public_key}
        '''
        result = self._values.get("mongodb_atlas_api_public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_atlas_project_id(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas project ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_atlas_project_id DynamicSecretMongodb#mongodb_atlas_project_id}
        '''
        result = self._values.get("mongodb_atlas_project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_default_auth_db(self) -> typing.Optional[builtins.str]:
        '''MongoDB server default authentication database.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_default_auth_db DynamicSecretMongodb#mongodb_default_auth_db}
        '''
        result = self._values.get("mongodb_default_auth_db")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_host_port(self) -> typing.Optional[builtins.str]:
        '''host:port (e.g. my.mongo.db:27017).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_host_port DynamicSecretMongodb#mongodb_host_port}
        '''
        result = self._values.get("mongodb_host_port")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_name(self) -> typing.Optional[builtins.str]:
        '''MongoDB name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_name DynamicSecretMongodb#mongodb_name}
        '''
        result = self._values.get("mongodb_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_password(self) -> typing.Optional[builtins.str]:
        '''MongoDB server password.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_password DynamicSecretMongodb#mongodb_password}
        '''
        result = self._values.get("mongodb_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_roles(self) -> typing.Optional[builtins.str]:
        '''MongoDB roles (e.g. MongoDB:[{role:readWrite, db: sales}], MongoDB Atlas:[{roleName : readWrite, databaseName: sales}]).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_roles DynamicSecretMongodb#mongodb_roles}
        '''
        result = self._values.get("mongodb_roles")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_server_uri(self) -> typing.Optional[builtins.str]:
        '''MongoDB server URI (e.g. mongodb://user:password@my.mongo.db:27017/admin?replicaSet=mySet).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_server_uri DynamicSecretMongodb#mongodb_server_uri}
        '''
        result = self._values.get("mongodb_server_uri")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_uri_options(self) -> typing.Optional[builtins.str]:
        '''MongoDB server URI options (e.g. replicaSet=mySet&authSource=authDB).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_uri_options DynamicSecretMongodb#mongodb_uri_options}
        '''
        result = self._values.get("mongodb_uri_options")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mongodb_username(self) -> typing.Optional[builtins.str]:
        '''MongoDB server username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#mongodb_username DynamicSecretMongodb#mongodb_username}
        '''
        result = self._values.get("mongodb_username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password_length(self) -> typing.Optional[builtins.str]:
        '''The length of the password to be generated.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#password_length DynamicSecretMongodb#password_length}
        '''
        result = self._values.get("password_length")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_bastion_issuer(self) -> typing.Optional[builtins.str]:
        '''Path to the SSH Certificate Issuer for your Akeyless Bastion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_bastion_issuer DynamicSecretMongodb#secure_access_bastion_issuer}
        '''
        result = self._values.get("secure_access_bastion_issuer")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_db_name(self) -> typing.Optional[builtins.str]:
        '''The DB name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_db_name DynamicSecretMongodb#secure_access_db_name}
        '''
        result = self._values.get("secure_access_db_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_enable(self) -> typing.Optional[builtins.str]:
        '''Enable/Disable secure remote access, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_enable DynamicSecretMongodb#secure_access_enable}
        '''
        result = self._values.get("secure_access_enable")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secure_access_host(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Target DB servers for connections., For multiple values repeat this flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_host DynamicSecretMongodb#secure_access_host}
        '''
        result = self._values.get("secure_access_host")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def secure_access_web(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Web Secure Remote Access.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#secure_access_web DynamicSecretMongodb#secure_access_web}
        '''
        result = self._values.get("secure_access_web")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: -t Tag1 -t Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#tags DynamicSecretMongodb#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in dynamic secret creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#target_name DynamicSecretMongodb#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL (e.g. 60s, 60m, 60h).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/dynamic_secret_mongodb#user_ttl DynamicSecretMongodb#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamicSecretMongodbConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamicSecretMongodb",
    "DynamicSecretMongodbConfig",
]

publication.publish()

def _typecheckingstub__846bf15c981dfa6246806cd102ae7a73629f2d4449e79650821e3802af3eccd9(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    custom_username_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
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
    password_length: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__5a64881ca4f819fed446dfc27402fca747d2aed9f869ab13fb7bc6b394f14ac2(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c79da567694f9445546ec680ef52a33956417c2dfebf007aac342e24ce6385bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc46ae4eada89dbf1cc5efd664879fd066c239e3f0d778210475dced46ec66e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eab8054584b7e0fcfe8fc2b12bd48593c36935291488e7b5fdc7570765b830e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5070e77eb322e1695fa09dd78da55721686f1c5166f8ac9c825b13dccf84892(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f53ad833fbb147c0a5b94e6baabfe3d73b8c9962dec3a5f5d4a233d2417a979f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c895a09950c33623d0d2d189f82f3a8f2143e6594c95e152bba1c61457877f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8da568b4cfe20630c5fd5c03fa65a9361e382c7ed4293cf3956da5e2584a90d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cad6f83ff06743d65f1dbc4960266aa5b8b710c216714f57fbdc8a5bd8482a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20109c4a5799c54183b2e47d57f7079d1207d14aad3ffe5400c729e166891d87(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c06d858165ccc0ff9cd053f2444ce975c154d8e80ca76e7cd4410f42bcd5d28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51a5f6aefee851ee021ee76daeb1422c11ad7caebff8b92c6ca7a71415093d02(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab49a0867cc73b7e1aa4533deebe243e7233893fe082d1935a2047c0090caf92(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3101b5600d36be2dc05fa3ca85e17bbcf8444020f9f77e311b700951702788a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e48e6340608df6a7c39c675503bb03103e187f930819e616aa60fcd26a05209(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16c4034ac1d38db82c19cb3db258b6f0b27b57ae8bd273d5130ed449aff067d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__590a9ac709acc22fc0621af631e28654c0a0d201cfdf966ebd05a76efcc41c8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c577949cf77e5036c7da8ff1bc15c31e3fdd5c51f9c1a593e751ad73137280e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5bcb7231039944616ac7aa0e2b47b1614282a57bddde6c3365e73cc84290e46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b72055ad9e1180be326ac7ec197dbf5c85765cddf5fcd97e5d6d8bdcf434a121(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b29505a9340bc97cd04d8e63d3e7643f515a0efa858dec0590e342fba7857f8d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba909b192bbe164e3e72729a6c75264412fafecf7e23c60cba83e8bdd2d7a473(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e28c588031f31d76e4871b008d4cfdf8715b9c858222286f31ff9d5701cc8f5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73f21a0c8ab4e9f75efef071501a4f150686c38498adf77b41ea5943be459f3c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0e9dfd0105f99f5b9a0ec13f427604d3d57df3571b14760a38e5fd050e80877(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18a5ed1ef326ec173fd4e520d1a4484694b0a60a6b0af55f758a857d44e2a529(
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
    encryption_key_name: typing.Optional[builtins.str] = None,
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
    password_length: typing.Optional[builtins.str] = None,
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
