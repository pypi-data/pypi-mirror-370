'''
# `akeyless_gateway_cache`

Refer to the Terraform Registry for docs: [`akeyless_gateway_cache`](https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache).
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


class GatewayCache(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="akeyless.gatewayCache.GatewayCache",
):
    '''Represents a {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache akeyless_gateway_cache}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        backup_interval: typing.Optional[builtins.str] = None,
        enable_cache: typing.Optional[builtins.str] = None,
        enable_proactive: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        minimum_fetch_interval: typing.Optional[builtins.str] = None,
        stale_timeout: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache akeyless_gateway_cache} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param backup_interval: Secure backup interval in minutes. To ensure service continuity in case of power cycle and network outage secrets will be backed up periodically per backup interval Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#backup_interval GatewayCache#backup_interval}
        :param enable_cache: Enable cache [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#enable_cache GatewayCache#enable_cache}
        :param enable_proactive: Enable proactive caching [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#enable_proactive GatewayCache#enable_proactive}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#id GatewayCache#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param minimum_fetch_interval: When using Cache or/and Proactive Cache, additional secrets will be fetched upon requesting a secret, based on the requestor's access policy. Define minimum fetching interval to avoid over fetching in a given time frame Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#minimum_fetch_interval GatewayCache#minimum_fetch_interval}
        :param stale_timeout: Stale timeout in minutes, cache entries which are not accessed within timeout will be removed from cache. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#stale_timeout GatewayCache#stale_timeout}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a0c540cdaf43d8b6d41b43a8745d4cdce47c79125ca2dec8184d788510b303d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GatewayCacheConfig(
            backup_interval=backup_interval,
            enable_cache=enable_cache,
            enable_proactive=enable_proactive,
            id=id,
            minimum_fetch_interval=minimum_fetch_interval,
            stale_timeout=stale_timeout,
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
        '''Generates CDKTF code for importing a GatewayCache resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GatewayCache to import.
        :param import_from_id: The id of the existing GatewayCache that should be imported. Refer to the {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GatewayCache to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__040c9d6c68a032da9c19088a2397d3688164b1c6ff04ca2ba4549ca483d6a753)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackupInterval")
    def reset_backup_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupInterval", []))

    @jsii.member(jsii_name="resetEnableCache")
    def reset_enable_cache(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableCache", []))

    @jsii.member(jsii_name="resetEnableProactive")
    def reset_enable_proactive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableProactive", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetMinimumFetchInterval")
    def reset_minimum_fetch_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumFetchInterval", []))

    @jsii.member(jsii_name="resetStaleTimeout")
    def reset_stale_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaleTimeout", []))

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
    @jsii.member(jsii_name="backupIntervalInput")
    def backup_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="enableCacheInput")
    def enable_cache_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enableCacheInput"))

    @builtins.property
    @jsii.member(jsii_name="enableProactiveInput")
    def enable_proactive_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "enableProactiveInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumFetchIntervalInput")
    def minimum_fetch_interval_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumFetchIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="staleTimeoutInput")
    def stale_timeout_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staleTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="backupInterval")
    def backup_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupInterval"))

    @backup_interval.setter
    def backup_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82ded18a1479c4dd57b4d8a3de82daf437bf43ee24ca21020e35adad512aa085)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupInterval", value)

    @builtins.property
    @jsii.member(jsii_name="enableCache")
    def enable_cache(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enableCache"))

    @enable_cache.setter
    def enable_cache(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84ca93fa9f71ab16621fddf7fe65105e98f49e45a1972b207cb983a5a66e3f82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableCache", value)

    @builtins.property
    @jsii.member(jsii_name="enableProactive")
    def enable_proactive(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "enableProactive"))

    @enable_proactive.setter
    def enable_proactive(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a47f8ba7095f411dcce6d7a09400c822ffa49189d23fc415d83052f271c73aeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableProactive", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb9cf3c2ab5aba57d0c7d39aa15d642124ef28de0af69eb1521f54342945fa77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="minimumFetchInterval")
    def minimum_fetch_interval(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumFetchInterval"))

    @minimum_fetch_interval.setter
    def minimum_fetch_interval(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5af52140c18716c2ec5da4a353aa9875ef29e2d673fdfce113cfe09e31864991)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumFetchInterval", value)

    @builtins.property
    @jsii.member(jsii_name="staleTimeout")
    def stale_timeout(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staleTimeout"))

    @stale_timeout.setter
    def stale_timeout(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__180a200891aaed04ae0fe37e38c63afc87e4756181b96fd710ec47699aa1b063)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staleTimeout", value)


@jsii.data_type(
    jsii_type="akeyless.gatewayCache.GatewayCacheConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "backup_interval": "backupInterval",
        "enable_cache": "enableCache",
        "enable_proactive": "enableProactive",
        "id": "id",
        "minimum_fetch_interval": "minimumFetchInterval",
        "stale_timeout": "staleTimeout",
    },
)
class GatewayCacheConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backup_interval: typing.Optional[builtins.str] = None,
        enable_cache: typing.Optional[builtins.str] = None,
        enable_proactive: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        minimum_fetch_interval: typing.Optional[builtins.str] = None,
        stale_timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param backup_interval: Secure backup interval in minutes. To ensure service continuity in case of power cycle and network outage secrets will be backed up periodically per backup interval Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#backup_interval GatewayCache#backup_interval}
        :param enable_cache: Enable cache [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#enable_cache GatewayCache#enable_cache}
        :param enable_proactive: Enable proactive caching [true/false]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#enable_proactive GatewayCache#enable_proactive}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#id GatewayCache#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param minimum_fetch_interval: When using Cache or/and Proactive Cache, additional secrets will be fetched upon requesting a secret, based on the requestor's access policy. Define minimum fetching interval to avoid over fetching in a given time frame Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#minimum_fetch_interval GatewayCache#minimum_fetch_interval}
        :param stale_timeout: Stale timeout in minutes, cache entries which are not accessed within timeout will be removed from cache. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#stale_timeout GatewayCache#stale_timeout}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a074764b774d38bcc0c615d7a262bb1438998176f971e550aaf65f14424b6d9)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument backup_interval", value=backup_interval, expected_type=type_hints["backup_interval"])
            check_type(argname="argument enable_cache", value=enable_cache, expected_type=type_hints["enable_cache"])
            check_type(argname="argument enable_proactive", value=enable_proactive, expected_type=type_hints["enable_proactive"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument minimum_fetch_interval", value=minimum_fetch_interval, expected_type=type_hints["minimum_fetch_interval"])
            check_type(argname="argument stale_timeout", value=stale_timeout, expected_type=type_hints["stale_timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
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
        if backup_interval is not None:
            self._values["backup_interval"] = backup_interval
        if enable_cache is not None:
            self._values["enable_cache"] = enable_cache
        if enable_proactive is not None:
            self._values["enable_proactive"] = enable_proactive
        if id is not None:
            self._values["id"] = id
        if minimum_fetch_interval is not None:
            self._values["minimum_fetch_interval"] = minimum_fetch_interval
        if stale_timeout is not None:
            self._values["stale_timeout"] = stale_timeout

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
    def backup_interval(self) -> typing.Optional[builtins.str]:
        '''Secure backup interval in minutes.

        To ensure service continuity in case of power cycle and network outage secrets will be backed up periodically per backup interval

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#backup_interval GatewayCache#backup_interval}
        '''
        result = self._values.get("backup_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_cache(self) -> typing.Optional[builtins.str]:
        '''Enable cache [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#enable_cache GatewayCache#enable_cache}
        '''
        result = self._values.get("enable_cache")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_proactive(self) -> typing.Optional[builtins.str]:
        '''Enable proactive caching [true/false].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#enable_proactive GatewayCache#enable_proactive}
        '''
        result = self._values.get("enable_proactive")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#id GatewayCache#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minimum_fetch_interval(self) -> typing.Optional[builtins.str]:
        '''When using Cache or/and Proactive Cache, additional secrets will be fetched upon requesting a secret, based on the requestor's access policy.

        Define minimum fetching interval to avoid over fetching in a given time frame

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#minimum_fetch_interval GatewayCache#minimum_fetch_interval}
        '''
        result = self._values.get("minimum_fetch_interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stale_timeout(self) -> typing.Optional[builtins.str]:
        '''Stale timeout in minutes, cache entries which are not accessed within timeout will be removed from cache.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/akeyless-community/akeyless/1.10.3/docs/resources/gateway_cache#stale_timeout GatewayCache#stale_timeout}
        '''
        result = self._values.get("stale_timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GatewayCacheConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GatewayCache",
    "GatewayCacheConfig",
]

publication.publish()

def _typecheckingstub__0a0c540cdaf43d8b6d41b43a8745d4cdce47c79125ca2dec8184d788510b303d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    backup_interval: typing.Optional[builtins.str] = None,
    enable_cache: typing.Optional[builtins.str] = None,
    enable_proactive: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    minimum_fetch_interval: typing.Optional[builtins.str] = None,
    stale_timeout: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__040c9d6c68a032da9c19088a2397d3688164b1c6ff04ca2ba4549ca483d6a753(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82ded18a1479c4dd57b4d8a3de82daf437bf43ee24ca21020e35adad512aa085(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84ca93fa9f71ab16621fddf7fe65105e98f49e45a1972b207cb983a5a66e3f82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a47f8ba7095f411dcce6d7a09400c822ffa49189d23fc415d83052f271c73aeb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb9cf3c2ab5aba57d0c7d39aa15d642124ef28de0af69eb1521f54342945fa77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5af52140c18716c2ec5da4a353aa9875ef29e2d673fdfce113cfe09e31864991(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__180a200891aaed04ae0fe37e38c63afc87e4756181b96fd710ec47699aa1b063(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a074764b774d38bcc0c615d7a262bb1438998176f971e550aaf65f14424b6d9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    backup_interval: typing.Optional[builtins.str] = None,
    enable_cache: typing.Optional[builtins.str] = None,
    enable_proactive: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    minimum_fetch_interval: typing.Optional[builtins.str] = None,
    stale_timeout: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
