'''
# `akeyless_producer_gcp`

Refer to the Terraform Registry for docs: [`akeyless_producer_gcp`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp).
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


class ProducerGcp(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.producerGcp.ProducerGcp",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp akeyless_producer_gcp}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        delete_protection: typing.Optional[builtins.str] = None,
        gcp_cred_type: typing.Optional[builtins.str] = None,
        gcp_key: typing.Optional[builtins.str] = None,
        gcp_key_algo: typing.Optional[builtins.str] = None,
        gcp_sa_email: typing.Optional[builtins.str] = None,
        gcp_token_scopes: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        role_binding: typing.Optional[builtins.str] = None,
        service_account_type: typing.Optional[builtins.str] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp akeyless_producer_gcp} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#name ProducerGcp#name}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#delete_protection ProducerGcp#delete_protection}
        :param gcp_cred_type: Credentials type, options are [token, key]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_cred_type ProducerGcp#gcp_cred_type}
        :param gcp_key: Base64-encoded service account private key text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_key ProducerGcp#gcp_key}
        :param gcp_key_algo: Service account key algorithm, e.g. KEY_ALG_RSA_1024. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_key_algo ProducerGcp#gcp_key_algo}
        :param gcp_sa_email: GCP service account email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_sa_email ProducerGcp#gcp_sa_email}
        :param gcp_token_scopes: Access token scopes list, e.g. scope1,scope2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_token_scopes ProducerGcp#gcp_token_scopes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#id ProducerGcp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Dynamic producer encryption key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#producer_encryption_key_name ProducerGcp#producer_encryption_key_name}
        :param role_binding: Role binding definitions in json format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#role_binding ProducerGcp#role_binding}
        :param service_account_type: The type of the gcp dynamic secret. Options[fixed, dynamic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#service_account_type ProducerGcp#service_account_type}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#tags ProducerGcp#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#target_name ProducerGcp#target_name}
        :param user_ttl: User TTL (<=60m for access token). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#user_ttl ProducerGcp#user_ttl}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d54577dd84614e87738468349c753e7cae2a1c6979ca70d8053ffe7b7cead988)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ProducerGcpConfig(
            name=name,
            delete_protection=delete_protection,
            gcp_cred_type=gcp_cred_type,
            gcp_key=gcp_key,
            gcp_key_algo=gcp_key_algo,
            gcp_sa_email=gcp_sa_email,
            gcp_token_scopes=gcp_token_scopes,
            id=id,
            producer_encryption_key_name=producer_encryption_key_name,
            role_binding=role_binding,
            service_account_type=service_account_type,
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
        '''Generates CDKTF code for importing a ProducerGcp resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ProducerGcp to import.
        :param import_from_id: The id of the existing ProducerGcp that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ProducerGcp to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac4291ddcca5e3ae785c07d0e10d637c2f764ccda7501441181c304860ae92ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetGcpCredType")
    def reset_gcp_cred_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpCredType", []))

    @jsii.member(jsii_name="resetGcpKey")
    def reset_gcp_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpKey", []))

    @jsii.member(jsii_name="resetGcpKeyAlgo")
    def reset_gcp_key_algo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpKeyAlgo", []))

    @jsii.member(jsii_name="resetGcpSaEmail")
    def reset_gcp_sa_email(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpSaEmail", []))

    @jsii.member(jsii_name="resetGcpTokenScopes")
    def reset_gcp_token_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpTokenScopes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProducerEncryptionKeyName")
    def reset_producer_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProducerEncryptionKeyName", []))

    @jsii.member(jsii_name="resetRoleBinding")
    def reset_role_binding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleBinding", []))

    @jsii.member(jsii_name="resetServiceAccountType")
    def reset_service_account_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountType", []))

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
    @jsii.member(jsii_name="gcpCredTypeInput")
    def gcp_cred_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpCredTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpKeyAlgoInput")
    def gcp_key_algo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpKeyAlgoInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpKeyInput")
    def gcp_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpSaEmailInput")
    def gcp_sa_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpSaEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpTokenScopesInput")
    def gcp_token_scopes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpTokenScopesInput"))

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
    @jsii.member(jsii_name="roleBindingInput")
    def role_binding_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleBindingInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountTypeInput")
    def service_account_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountTypeInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__b1f3d615257eb33c53abe0e5cb6b3c0faa7cbefd62468718c81ed6f30dc0fc3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="gcpCredType")
    def gcp_cred_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpCredType"))

    @gcp_cred_type.setter
    def gcp_cred_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d87217ff75d3fdb29132dfd28634cdb6f8e0d38c446b5c7a90fd56aa9b04e34d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpCredType", value)

    @builtins.property
    @jsii.member(jsii_name="gcpKey")
    def gcp_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpKey"))

    @gcp_key.setter
    def gcp_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4cd5220dac5f47f1873ac93adddce5b6adab15a7494bad7891ab0d7b7d49bfc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpKey", value)

    @builtins.property
    @jsii.member(jsii_name="gcpKeyAlgo")
    def gcp_key_algo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpKeyAlgo"))

    @gcp_key_algo.setter
    def gcp_key_algo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff7f11ff31c5a9cbe70b9ee6ff83b302c5a089db7cbf678ee6b4bf297f173c20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpKeyAlgo", value)

    @builtins.property
    @jsii.member(jsii_name="gcpSaEmail")
    def gcp_sa_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpSaEmail"))

    @gcp_sa_email.setter
    def gcp_sa_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10c4727f9c333fa1fb376ffb8756535dbd6972c41ff71584449f782934b48ea8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpSaEmail", value)

    @builtins.property
    @jsii.member(jsii_name="gcpTokenScopes")
    def gcp_token_scopes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpTokenScopes"))

    @gcp_token_scopes.setter
    def gcp_token_scopes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b4a7e2b16aae5f8564189482fab5126a0c2cd936ed4fe8407bffbc4df9e7cb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpTokenScopes", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acfa33e72d5a3d608d343cdcda8dd1901af30ff6d149583b71a67cfcf4370da0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6aa74005f0e2d434de8ae922221d6134b3bc4b5c69369e1eaf6e3b36dd4a0e04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="producerEncryptionKeyName")
    def producer_encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "producerEncryptionKeyName"))

    @producer_encryption_key_name.setter
    def producer_encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15efe4a996e03ed098b56a8acce7f2967d377b491ccc503af442c3b1d1bed2aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "producerEncryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="roleBinding")
    def role_binding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleBinding"))

    @role_binding.setter
    def role_binding(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd6eb30e189de47a5119db6ca7216561555126dd7342bb618e65dea95eaa82ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleBinding", value)

    @builtins.property
    @jsii.member(jsii_name="serviceAccountType")
    def service_account_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountType"))

    @service_account_type.setter
    def service_account_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c6d0a642eb82d51c2c4752e7348effb635088d608f3e841437b3279444be6d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountType", value)

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e20a99170a604dcd3dfab70d0c7a0ae7bb0f6878e17e697525b76fa2d510eded)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value)

    @builtins.property
    @jsii.member(jsii_name="targetName")
    def target_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetName"))

    @target_name.setter
    def target_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7791bdb23e49a1b7456278c22e02e8d55a3778281930158ac1c496b02deea3f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetName", value)

    @builtins.property
    @jsii.member(jsii_name="userTtl")
    def user_ttl(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userTtl"))

    @user_ttl.setter
    def user_ttl(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__084bf68fb5ea0ebe69962a65f109e98e8f9000f7aaf5ff95304b573d9d9fdd9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userTtl", value)


@jsii.data_type(
    jsii_type="akeyless.producerGcp.ProducerGcpConfig",
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
        "gcp_cred_type": "gcpCredType",
        "gcp_key": "gcpKey",
        "gcp_key_algo": "gcpKeyAlgo",
        "gcp_sa_email": "gcpSaEmail",
        "gcp_token_scopes": "gcpTokenScopes",
        "id": "id",
        "producer_encryption_key_name": "producerEncryptionKeyName",
        "role_binding": "roleBinding",
        "service_account_type": "serviceAccountType",
        "tags": "tags",
        "target_name": "targetName",
        "user_ttl": "userTtl",
    },
)
class ProducerGcpConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        gcp_cred_type: typing.Optional[builtins.str] = None,
        gcp_key: typing.Optional[builtins.str] = None,
        gcp_key_algo: typing.Optional[builtins.str] = None,
        gcp_sa_email: typing.Optional[builtins.str] = None,
        gcp_token_scopes: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        producer_encryption_key_name: typing.Optional[builtins.str] = None,
        role_binding: typing.Optional[builtins.str] = None,
        service_account_type: typing.Optional[builtins.str] = None,
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
        :param name: Producer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#name ProducerGcp#name}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#delete_protection ProducerGcp#delete_protection}
        :param gcp_cred_type: Credentials type, options are [token, key]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_cred_type ProducerGcp#gcp_cred_type}
        :param gcp_key: Base64-encoded service account private key text. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_key ProducerGcp#gcp_key}
        :param gcp_key_algo: Service account key algorithm, e.g. KEY_ALG_RSA_1024. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_key_algo ProducerGcp#gcp_key_algo}
        :param gcp_sa_email: GCP service account email. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_sa_email ProducerGcp#gcp_sa_email}
        :param gcp_token_scopes: Access token scopes list, e.g. scope1,scope2. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_token_scopes ProducerGcp#gcp_token_scopes}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#id ProducerGcp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param producer_encryption_key_name: Dynamic producer encryption key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#producer_encryption_key_name ProducerGcp#producer_encryption_key_name}
        :param role_binding: Role binding definitions in json format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#role_binding ProducerGcp#role_binding}
        :param service_account_type: The type of the gcp dynamic secret. Options[fixed, dynamic]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#service_account_type ProducerGcp#service_account_type}
        :param tags: List of the tags attached to this secret. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#tags ProducerGcp#tags}
        :param target_name: Name of existing target to use in producer creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#target_name ProducerGcp#target_name}
        :param user_ttl: User TTL (<=60m for access token). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#user_ttl ProducerGcp#user_ttl}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__700ae0caf09482320bfa4fc0e9e54bbfc55e5d3eda9fbc4d8ae56b362f2a6326)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument gcp_cred_type", value=gcp_cred_type, expected_type=type_hints["gcp_cred_type"])
            check_type(argname="argument gcp_key", value=gcp_key, expected_type=type_hints["gcp_key"])
            check_type(argname="argument gcp_key_algo", value=gcp_key_algo, expected_type=type_hints["gcp_key_algo"])
            check_type(argname="argument gcp_sa_email", value=gcp_sa_email, expected_type=type_hints["gcp_sa_email"])
            check_type(argname="argument gcp_token_scopes", value=gcp_token_scopes, expected_type=type_hints["gcp_token_scopes"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument producer_encryption_key_name", value=producer_encryption_key_name, expected_type=type_hints["producer_encryption_key_name"])
            check_type(argname="argument role_binding", value=role_binding, expected_type=type_hints["role_binding"])
            check_type(argname="argument service_account_type", value=service_account_type, expected_type=type_hints["service_account_type"])
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
        if gcp_cred_type is not None:
            self._values["gcp_cred_type"] = gcp_cred_type
        if gcp_key is not None:
            self._values["gcp_key"] = gcp_key
        if gcp_key_algo is not None:
            self._values["gcp_key_algo"] = gcp_key_algo
        if gcp_sa_email is not None:
            self._values["gcp_sa_email"] = gcp_sa_email
        if gcp_token_scopes is not None:
            self._values["gcp_token_scopes"] = gcp_token_scopes
        if id is not None:
            self._values["id"] = id
        if producer_encryption_key_name is not None:
            self._values["producer_encryption_key_name"] = producer_encryption_key_name
        if role_binding is not None:
            self._values["role_binding"] = role_binding
        if service_account_type is not None:
            self._values["service_account_type"] = service_account_type
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#name ProducerGcp#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this item, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#delete_protection ProducerGcp#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_cred_type(self) -> typing.Optional[builtins.str]:
        '''Credentials type, options are [token, key].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_cred_type ProducerGcp#gcp_cred_type}
        '''
        result = self._values.get("gcp_cred_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_key(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded service account private key text.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_key ProducerGcp#gcp_key}
        '''
        result = self._values.get("gcp_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_key_algo(self) -> typing.Optional[builtins.str]:
        '''Service account key algorithm, e.g. KEY_ALG_RSA_1024.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_key_algo ProducerGcp#gcp_key_algo}
        '''
        result = self._values.get("gcp_key_algo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_sa_email(self) -> typing.Optional[builtins.str]:
        '''GCP service account email.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_sa_email ProducerGcp#gcp_sa_email}
        '''
        result = self._values.get("gcp_sa_email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_token_scopes(self) -> typing.Optional[builtins.str]:
        '''Access token scopes list, e.g. scope1,scope2.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#gcp_token_scopes ProducerGcp#gcp_token_scopes}
        '''
        result = self._values.get("gcp_token_scopes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#id ProducerGcp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def producer_encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''Dynamic producer encryption key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#producer_encryption_key_name ProducerGcp#producer_encryption_key_name}
        '''
        result = self._values.get("producer_encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_binding(self) -> typing.Optional[builtins.str]:
        '''Role binding definitions in json format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#role_binding ProducerGcp#role_binding}
        '''
        result = self._values.get("role_binding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_account_type(self) -> typing.Optional[builtins.str]:
        '''The type of the gcp dynamic secret. Options[fixed, dynamic].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#service_account_type ProducerGcp#service_account_type}
        '''
        result = self._values.get("service_account_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this secret.

        To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#tags ProducerGcp#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target_name(self) -> typing.Optional[builtins.str]:
        '''Name of existing target to use in producer creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#target_name ProducerGcp#target_name}
        '''
        result = self._values.get("target_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_ttl(self) -> typing.Optional[builtins.str]:
        '''User TTL (<=60m for access token).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/producer_gcp#user_ttl ProducerGcp#user_ttl}
        '''
        result = self._values.get("user_ttl")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProducerGcpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ProducerGcp",
    "ProducerGcpConfig",
]

publication.publish()

def _typecheckingstub__d54577dd84614e87738468349c753e7cae2a1c6979ca70d8053ffe7b7cead988(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    delete_protection: typing.Optional[builtins.str] = None,
    gcp_cred_type: typing.Optional[builtins.str] = None,
    gcp_key: typing.Optional[builtins.str] = None,
    gcp_key_algo: typing.Optional[builtins.str] = None,
    gcp_sa_email: typing.Optional[builtins.str] = None,
    gcp_token_scopes: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    role_binding: typing.Optional[builtins.str] = None,
    service_account_type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__ac4291ddcca5e3ae785c07d0e10d637c2f764ccda7501441181c304860ae92ef(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1f3d615257eb33c53abe0e5cb6b3c0faa7cbefd62468718c81ed6f30dc0fc3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d87217ff75d3fdb29132dfd28634cdb6f8e0d38c446b5c7a90fd56aa9b04e34d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4cd5220dac5f47f1873ac93adddce5b6adab15a7494bad7891ab0d7b7d49bfc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff7f11ff31c5a9cbe70b9ee6ff83b302c5a089db7cbf678ee6b4bf297f173c20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10c4727f9c333fa1fb376ffb8756535dbd6972c41ff71584449f782934b48ea8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b4a7e2b16aae5f8564189482fab5126a0c2cd936ed4fe8407bffbc4df9e7cb0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acfa33e72d5a3d608d343cdcda8dd1901af30ff6d149583b71a67cfcf4370da0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6aa74005f0e2d434de8ae922221d6134b3bc4b5c69369e1eaf6e3b36dd4a0e04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15efe4a996e03ed098b56a8acce7f2967d377b491ccc503af442c3b1d1bed2aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd6eb30e189de47a5119db6ca7216561555126dd7342bb618e65dea95eaa82ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c6d0a642eb82d51c2c4752e7348effb635088d608f3e841437b3279444be6d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e20a99170a604dcd3dfab70d0c7a0ae7bb0f6878e17e697525b76fa2d510eded(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7791bdb23e49a1b7456278c22e02e8d55a3778281930158ac1c496b02deea3f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__084bf68fb5ea0ebe69962a65f109e98e8f9000f7aaf5ff95304b573d9d9fdd9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__700ae0caf09482320bfa4fc0e9e54bbfc55e5d3eda9fbc4d8ae56b362f2a6326(
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
    gcp_cred_type: typing.Optional[builtins.str] = None,
    gcp_key: typing.Optional[builtins.str] = None,
    gcp_key_algo: typing.Optional[builtins.str] = None,
    gcp_sa_email: typing.Optional[builtins.str] = None,
    gcp_token_scopes: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    producer_encryption_key_name: typing.Optional[builtins.str] = None,
    role_binding: typing.Optional[builtins.str] = None,
    service_account_type: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    target_name: typing.Optional[builtins.str] = None,
    user_ttl: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
