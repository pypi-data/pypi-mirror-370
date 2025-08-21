'''
# `akeyless_tokenizer`

Refer to the Terraform Registry for docs: [`akeyless_tokenizer`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer).
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


class Tokenizer(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.tokenizer.Tokenizer",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer akeyless_tokenizer}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        template_type: builtins.str,
        alphabet: typing.Optional[builtins.str] = None,
        decoding_template: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        encoding_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        pattern: typing.Optional[builtins.str] = None,
        tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        tokenizer_type: typing.Optional[builtins.str] = None,
        tweak_type: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer akeyless_tokenizer} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Tokenizer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#name Tokenizer#name}
        :param template_type: Which template type this tokenizer is used for [SSN,CreditCard,USPhoneNumber,Custom]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#template_type Tokenizer#template_type}
        :param alphabet: Alphabet to use in custom vaultless tokenization, such as '0123456789' for credit cards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#alphabet Tokenizer#alphabet}
        :param decoding_template: The Decoding output template to use in custom vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#decoding_template Tokenizer#decoding_template}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#delete_protection Tokenizer#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#description Tokenizer#description}
        :param encoding_template: The Encoding output template to use in custom vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#encoding_template Tokenizer#encoding_template}
        :param encryption_key_name: AES key name to use in vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#encryption_key_name Tokenizer#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#id Tokenizer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param pattern: Pattern to use in custom vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#pattern Tokenizer#pattern}
        :param tag: List of the tags attached to this key. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tag Tokenizer#tag}
        :param tokenizer_type: Tokenizer type(vaultless). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tokenizer_type Tokenizer#tokenizer_type}
        :param tweak_type: The tweak type to use in vaultless tokenization [Supplied, Generated, Internal, Masking]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tweak_type Tokenizer#tweak_type}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0768d713d1932569bfb3119f1292e2f318bc59a26eb37ce088c17ba7d75db43)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = TokenizerConfig(
            name=name,
            template_type=template_type,
            alphabet=alphabet,
            decoding_template=decoding_template,
            delete_protection=delete_protection,
            description=description,
            encoding_template=encoding_template,
            encryption_key_name=encryption_key_name,
            id=id,
            pattern=pattern,
            tag=tag,
            tokenizer_type=tokenizer_type,
            tweak_type=tweak_type,
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
        '''Generates CDKTF code for importing a Tokenizer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Tokenizer to import.
        :param import_from_id: The id of the existing Tokenizer that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Tokenizer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf1bde24ad39df4a2f3591d75e9725fe9a8fa51797e9732d744aa7bac0bf572)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlphabet")
    def reset_alphabet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlphabet", []))

    @jsii.member(jsii_name="resetDecodingTemplate")
    def reset_decoding_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDecodingTemplate", []))

    @jsii.member(jsii_name="resetDeleteProtection")
    def reset_delete_protection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteProtection", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetEncodingTemplate")
    def reset_encoding_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncodingTemplate", []))

    @jsii.member(jsii_name="resetEncryptionKeyName")
    def reset_encryption_key_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionKeyName", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPattern")
    def reset_pattern(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPattern", []))

    @jsii.member(jsii_name="resetTag")
    def reset_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTag", []))

    @jsii.member(jsii_name="resetTokenizerType")
    def reset_tokenizer_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokenizerType", []))

    @jsii.member(jsii_name="resetTweakType")
    def reset_tweak_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTweakType", []))

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
    @jsii.member(jsii_name="tweak")
    def tweak(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tweak"))

    @builtins.property
    @jsii.member(jsii_name="alphabetInput")
    def alphabet_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alphabetInput"))

    @builtins.property
    @jsii.member(jsii_name="decodingTemplateInput")
    def decoding_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "decodingTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteProtectionInput")
    def delete_protection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteProtectionInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="encodingTemplateInput")
    def encoding_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encodingTemplateInput"))

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
    @jsii.member(jsii_name="patternInput")
    def pattern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "patternInput"))

    @builtins.property
    @jsii.member(jsii_name="tagInput")
    def tag_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagInput"))

    @builtins.property
    @jsii.member(jsii_name="templateTypeInput")
    def template_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "templateTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenizerTypeInput")
    def tokenizer_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenizerTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="tweakTypeInput")
    def tweak_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tweakTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="alphabet")
    def alphabet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alphabet"))

    @alphabet.setter
    def alphabet(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cee62d8902225853f7adb719a7eddb54d7bb1d532be9748e041cdfa5aa051a24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alphabet", value)

    @builtins.property
    @jsii.member(jsii_name="decodingTemplate")
    def decoding_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "decodingTemplate"))

    @decoding_template.setter
    def decoding_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__888f32396e7b362fde4164a05eb3299f9ad5cc12949df9ed25e547be0a41d236)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "decodingTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="deleteProtection")
    def delete_protection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteProtection"))

    @delete_protection.setter
    def delete_protection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__912d2259e1d45e3911dcd48ac1ccfbdad35b67552e3739a5ffd5193d64b4e74f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteProtection", value)

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__307f6b38cf19fb1ec5a414d4d74d63fe703c08db57c580234c5cec0ce88de326)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value)

    @builtins.property
    @jsii.member(jsii_name="encodingTemplate")
    def encoding_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encodingTemplate"))

    @encoding_template.setter
    def encoding_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2ec53ebc77fbc00dc134d2ffe40451c7548d66ed59224ce26d9e60cde8181fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encodingTemplate", value)

    @builtins.property
    @jsii.member(jsii_name="encryptionKeyName")
    def encryption_key_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionKeyName"))

    @encryption_key_name.setter
    def encryption_key_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ed512a17b898b00abb32512e2228875a6230829cf391ff329bea495759435ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionKeyName", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2e04f883f9732494875292792ec6e7ba351484186c5f2576149e52d748d1002)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e216a433fc20de35e5b5d71f62f46f716ec4496323d5f71579baa980eb57a848)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="pattern")
    def pattern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pattern"))

    @pattern.setter
    def pattern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__865df306797eaaac0fd00745bbeeed4eacb7b59722aa02e0b80be794c0684ccc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pattern", value)

    @builtins.property
    @jsii.member(jsii_name="tag")
    def tag(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tag"))

    @tag.setter
    def tag(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2843b110c62a14d7bad49d5d9fdb8f9e21433ea9451b60fa9dae40688e496112)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tag", value)

    @builtins.property
    @jsii.member(jsii_name="templateType")
    def template_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "templateType"))

    @template_type.setter
    def template_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe185c1c771dc60f6428496d3304a21ee77ac353c602608c21ab7c64915c0897)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "templateType", value)

    @builtins.property
    @jsii.member(jsii_name="tokenizerType")
    def tokenizer_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tokenizerType"))

    @tokenizer_type.setter
    def tokenizer_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f4a39b00ceadecfbf992aed4fdb8fa6777198a99e3a5d96d59770cd1e4597a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokenizerType", value)

    @builtins.property
    @jsii.member(jsii_name="tweakType")
    def tweak_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tweakType"))

    @tweak_type.setter
    def tweak_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25f70374fbfa0d8e3e81e844c4b51b53f3f344930d82738cf548b01a194f13d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tweakType", value)


@jsii.data_type(
    jsii_type="akeyless.tokenizer.TokenizerConfig",
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
        "template_type": "templateType",
        "alphabet": "alphabet",
        "decoding_template": "decodingTemplate",
        "delete_protection": "deleteProtection",
        "description": "description",
        "encoding_template": "encodingTemplate",
        "encryption_key_name": "encryptionKeyName",
        "id": "id",
        "pattern": "pattern",
        "tag": "tag",
        "tokenizer_type": "tokenizerType",
        "tweak_type": "tweakType",
    },
)
class TokenizerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        template_type: builtins.str,
        alphabet: typing.Optional[builtins.str] = None,
        decoding_template: typing.Optional[builtins.str] = None,
        delete_protection: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        encoding_template: typing.Optional[builtins.str] = None,
        encryption_key_name: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        pattern: typing.Optional[builtins.str] = None,
        tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        tokenizer_type: typing.Optional[builtins.str] = None,
        tweak_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Tokenizer name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#name Tokenizer#name}
        :param template_type: Which template type this tokenizer is used for [SSN,CreditCard,USPhoneNumber,Custom]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#template_type Tokenizer#template_type}
        :param alphabet: Alphabet to use in custom vaultless tokenization, such as '0123456789' for credit cards. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#alphabet Tokenizer#alphabet}
        :param decoding_template: The Decoding output template to use in custom vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#decoding_template Tokenizer#decoding_template}
        :param delete_protection: Protection from accidental deletion of this item, [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#delete_protection Tokenizer#delete_protection}
        :param description: Description of the object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#description Tokenizer#description}
        :param encoding_template: The Encoding output template to use in custom vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#encoding_template Tokenizer#encoding_template}
        :param encryption_key_name: AES key name to use in vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#encryption_key_name Tokenizer#encryption_key_name}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#id Tokenizer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param pattern: Pattern to use in custom vaultless tokenization. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#pattern Tokenizer#pattern}
        :param tag: List of the tags attached to this key. To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2 Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tag Tokenizer#tag}
        :param tokenizer_type: Tokenizer type(vaultless). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tokenizer_type Tokenizer#tokenizer_type}
        :param tweak_type: The tweak type to use in vaultless tokenization [Supplied, Generated, Internal, Masking]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tweak_type Tokenizer#tweak_type}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6a851873a1ea3ed433afe3a5202766d15ff1dd355d469990abc7c3b60ba6e22)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument template_type", value=template_type, expected_type=type_hints["template_type"])
            check_type(argname="argument alphabet", value=alphabet, expected_type=type_hints["alphabet"])
            check_type(argname="argument decoding_template", value=decoding_template, expected_type=type_hints["decoding_template"])
            check_type(argname="argument delete_protection", value=delete_protection, expected_type=type_hints["delete_protection"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encoding_template", value=encoding_template, expected_type=type_hints["encoding_template"])
            check_type(argname="argument encryption_key_name", value=encryption_key_name, expected_type=type_hints["encryption_key_name"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument pattern", value=pattern, expected_type=type_hints["pattern"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
            check_type(argname="argument tokenizer_type", value=tokenizer_type, expected_type=type_hints["tokenizer_type"])
            check_type(argname="argument tweak_type", value=tweak_type, expected_type=type_hints["tweak_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "template_type": template_type,
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
        if alphabet is not None:
            self._values["alphabet"] = alphabet
        if decoding_template is not None:
            self._values["decoding_template"] = decoding_template
        if delete_protection is not None:
            self._values["delete_protection"] = delete_protection
        if description is not None:
            self._values["description"] = description
        if encoding_template is not None:
            self._values["encoding_template"] = encoding_template
        if encryption_key_name is not None:
            self._values["encryption_key_name"] = encryption_key_name
        if id is not None:
            self._values["id"] = id
        if pattern is not None:
            self._values["pattern"] = pattern
        if tag is not None:
            self._values["tag"] = tag
        if tokenizer_type is not None:
            self._values["tokenizer_type"] = tokenizer_type
        if tweak_type is not None:
            self._values["tweak_type"] = tweak_type

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
        '''Tokenizer name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#name Tokenizer#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_type(self) -> builtins.str:
        '''Which template type this tokenizer is used for [SSN,CreditCard,USPhoneNumber,Custom].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#template_type Tokenizer#template_type}
        '''
        result = self._values.get("template_type")
        assert result is not None, "Required property 'template_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alphabet(self) -> typing.Optional[builtins.str]:
        '''Alphabet to use in custom vaultless tokenization, such as '0123456789' for credit cards.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#alphabet Tokenizer#alphabet}
        '''
        result = self._values.get("alphabet")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def decoding_template(self) -> typing.Optional[builtins.str]:
        '''The Decoding output template to use in custom vaultless tokenization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#decoding_template Tokenizer#decoding_template}
        '''
        result = self._values.get("decoding_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_protection(self) -> typing.Optional[builtins.str]:
        '''Protection from accidental deletion of this item, [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#delete_protection Tokenizer#delete_protection}
        '''
        result = self._values.get("delete_protection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#description Tokenizer#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encoding_template(self) -> typing.Optional[builtins.str]:
        '''The Encoding output template to use in custom vaultless tokenization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#encoding_template Tokenizer#encoding_template}
        '''
        result = self._values.get("encoding_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key_name(self) -> typing.Optional[builtins.str]:
        '''AES key name to use in vaultless tokenization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#encryption_key_name Tokenizer#encryption_key_name}
        '''
        result = self._values.get("encryption_key_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#id Tokenizer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pattern(self) -> typing.Optional[builtins.str]:
        '''Pattern to use in custom vaultless tokenization.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#pattern Tokenizer#pattern}
        '''
        result = self._values.get("pattern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of the tags attached to this key.

        To specify multiple tags use argument multiple times: --tag Tag1 --tag Tag2

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tag Tokenizer#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tokenizer_type(self) -> typing.Optional[builtins.str]:
        '''Tokenizer type(vaultless).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tokenizer_type Tokenizer#tokenizer_type}
        '''
        result = self._values.get("tokenizer_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tweak_type(self) -> typing.Optional[builtins.str]:
        '''The tweak type to use in vaultless tokenization [Supplied, Generated, Internal, Masking].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/tokenizer#tweak_type Tokenizer#tweak_type}
        '''
        result = self._values.get("tweak_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TokenizerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Tokenizer",
    "TokenizerConfig",
]

publication.publish()

def _typecheckingstub__f0768d713d1932569bfb3119f1292e2f318bc59a26eb37ce088c17ba7d75db43(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    template_type: builtins.str,
    alphabet: typing.Optional[builtins.str] = None,
    decoding_template: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    encoding_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    pattern: typing.Optional[builtins.str] = None,
    tag: typing.Optional[typing.Sequence[builtins.str]] = None,
    tokenizer_type: typing.Optional[builtins.str] = None,
    tweak_type: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__8cf1bde24ad39df4a2f3591d75e9725fe9a8fa51797e9732d744aa7bac0bf572(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cee62d8902225853f7adb719a7eddb54d7bb1d532be9748e041cdfa5aa051a24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__888f32396e7b362fde4164a05eb3299f9ad5cc12949df9ed25e547be0a41d236(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912d2259e1d45e3911dcd48ac1ccfbdad35b67552e3739a5ffd5193d64b4e74f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__307f6b38cf19fb1ec5a414d4d74d63fe703c08db57c580234c5cec0ce88de326(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2ec53ebc77fbc00dc134d2ffe40451c7548d66ed59224ce26d9e60cde8181fb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ed512a17b898b00abb32512e2228875a6230829cf391ff329bea495759435ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2e04f883f9732494875292792ec6e7ba351484186c5f2576149e52d748d1002(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e216a433fc20de35e5b5d71f62f46f716ec4496323d5f71579baa980eb57a848(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__865df306797eaaac0fd00745bbeeed4eacb7b59722aa02e0b80be794c0684ccc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2843b110c62a14d7bad49d5d9fdb8f9e21433ea9451b60fa9dae40688e496112(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe185c1c771dc60f6428496d3304a21ee77ac353c602608c21ab7c64915c0897(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f4a39b00ceadecfbf992aed4fdb8fa6777198a99e3a5d96d59770cd1e4597a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25f70374fbfa0d8e3e81e844c4b51b53f3f344930d82738cf548b01a194f13d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6a851873a1ea3ed433afe3a5202766d15ff1dd355d469990abc7c3b60ba6e22(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    template_type: builtins.str,
    alphabet: typing.Optional[builtins.str] = None,
    decoding_template: typing.Optional[builtins.str] = None,
    delete_protection: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    encoding_template: typing.Optional[builtins.str] = None,
    encryption_key_name: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    pattern: typing.Optional[builtins.str] = None,
    tag: typing.Optional[typing.Sequence[builtins.str]] = None,
    tokenizer_type: typing.Optional[builtins.str] = None,
    tweak_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
