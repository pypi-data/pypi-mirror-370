from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_imagebuilder as _aws_cdk_aws_imagebuilder_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8
from ..constructs import (
    Ec2ImagePipeline as _Ec2ImagePipeline_08b5ca60,
    Ec2ImagePipelineBaseProps as _Ec2ImagePipelineBaseProps_b9c7b595,
)
from ..types import LambdaConfiguration as _LambdaConfiguration_9f8afc24


class ApiGatewayStaticHosting(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting",
):
    '''(experimental) A pattern that deploys resources to support the hosting of static assets within an AWS account.

    Unlike the normal pattern for static content hosting (Amazon S3 fronted by Amazon CloudFront), this pattern instead
    uses a combination of Amazon S3, AWS Lambda, and Amazon API Gateway. This can be useful for rapidly deploying a
    static website that follows best practices when Amazon CloudFront is not available.

    The construct also handles encryption for the framework resources using either a provided KMS key or an
    AWS managed key.

    There are two methods for exposing the URL to consumers - the default API execution endpoint or via a custom domain
    name setup.

    If using the default API execution endpoint, you must provide a base path as this will translate to the
    stage name of the REST API. You must also ensure that all relative links in the static content either reference
    the base path in URLs relative to the root (e.g. preceded by '/') or uses URLs that are relative to the current
    directory (e.g. no '/').

    If using the custom domain name, then you do not need to provide a base path and relative links in your static
    content will not require modification. You can choose to specify a base path with this option if so desired - in
    that case, similar rules regarding relative URLs in the static content above must be followed.

    :stability: experimental

    Example::

        import { ApiGatewayStaticHosting } from '@cdklabs/cdk-proserve-lib/patterns';
        import { EndpointType } from 'aws-cdk-lib/aws-apigateway';
        
        new ApiGatewayStaticHosting(this, 'MyWebsite', {
            asset: {
                id: 'Entry',
                path: join(__dirname, 'assets', 'website', 'dist'),
                spaIndexPageName: 'index.html'
            },
            domain: {
                basePath: 'public'
            },
            endpoint: {
                types: [EndpointType.REGIONAL]
            },
            retainStoreOnDeletion: true,
            versionTag: '1.0.2'
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        asset: typing.Union["ApiGatewayStaticHosting.Asset", typing.Dict[builtins.str, typing.Any]],
        domain: typing.Union[typing.Union["ApiGatewayStaticHosting.CustomDomainConfiguration", typing.Dict[builtins.str, typing.Any]], typing.Union["ApiGatewayStaticHosting.DefaultEndpointConfiguration", typing.Dict[builtins.str, typing.Any]]],
        access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        retain_store_on_deletion: typing.Optional[builtins.bool] = None,
        version_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Creates a new static hosting pattern.

        :param scope: Parent to which the pattern belongs.
        :param id: Unique identifier for this instance.
        :param asset: (experimental) Metadata about the static assets to host.
        :param domain: (experimental) Configuration information for the distribution endpoint that will be used to serve static content.
        :param access_logging_bucket: (experimental) Amazon S3 bucket where access logs should be stored. Default: undefined A new bucket will be created for storing access logs
        :param access_policy: (experimental) Resource access policy to define on the API itself to control who can invoke the endpoint.
        :param api_log_destination: (experimental) Destination where Amazon API Gateway logs can be sent.
        :param encryption: (experimental) Encryption key for protecting the framework resources. Default: undefined AWS service-managed encryption keys will be used where available
        :param endpoint: (experimental) Endpoint deployment information for the REST API. Default: undefined Will deploy an edge-optimized API
        :param lambda_configuration: (experimental) Optional configuration settings for the backend handler.
        :param retain_store_on_deletion: (experimental) Whether or not to retain the Amazon S3 bucket where static assets are deployed on stack deletion. Default: false The Amazon S3 bucket and all assets contained within will be deleted
        :param version_tag: (experimental) A version identifier to deploy to the Amazon S3 bucket to help with rapid identification of current deployment This will appear as ``metadata.json`` at the root of the bucket. Default: undefined No version information will be deployed to the Amazon S3 bucket

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__926e3ab1cdccdb34f4dc75a68890781e04a583c1ec8481b471267ea1ecbb3c22)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ApiGatewayStaticHostingProps(
            asset=asset,
            domain=domain,
            access_logging_bucket=access_logging_bucket,
            access_policy=access_policy,
            api_log_destination=api_log_destination,
            encryption=encryption,
            endpoint=endpoint,
            lambda_configuration=lambda_configuration,
            retain_store_on_deletion=retain_store_on_deletion,
            version_tag=version_tag,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="components")
    def components(self) -> "ApiGatewayStaticHosting.PatternComponents":
        '''(experimental) Provides access to the underlying components of the pattern as an escape hatch.

        WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
        behave as expected or designed. You do so at your own risk.

        :stability: experimental
        '''
        return typing.cast("ApiGatewayStaticHosting.PatternComponents", jsii.get(self, "components"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        '''(experimental) URL for the API that distributes the static content.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="customDomainNameAlias")
    def custom_domain_name_alias(self) -> typing.Optional[builtins.str]:
        '''(experimental) Alias domain name for the API that distributes the static content.

        This is only available if the custom domain name configuration was provided to the pattern. In that event, you
        would then create either a CNAME or ALIAS record in your DNS system that maps your custom domain name to this
        value.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customDomainNameAlias"))

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.Asset",
        jsii_struct_bases=[],
        name_mapping={
            "id": "id",
            "path": "path",
            "spa_index_page_name": "spaIndexPageName",
        },
    )
    class Asset:
        def __init__(
            self,
            *,
            id: builtins.str,
            path: typing.Union[builtins.str, typing.Sequence[builtins.str]],
            spa_index_page_name: typing.Optional[builtins.str] = None,
        ) -> None:
            '''(experimental) Static Asset Definition.

            :param id: (experimental) Unique identifier to delineate an asset from other assets.
            :param path: (experimental) Path(s) on the local file system to the static asset(s). Each path must be either a directory or zip containing the assets
            :param spa_index_page_name: (experimental) Name of the index page for a Single Page Application (SPA). This is used as a default key to load when the path provided does not map to a concrete static asset.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__95377bd339103860abda9142b547350593c2c75dc36900d1cafdbd3ed1452918)
                check_type(argname="argument id", value=id, expected_type=type_hints["id"])
                check_type(argname="argument path", value=path, expected_type=type_hints["path"])
                check_type(argname="argument spa_index_page_name", value=spa_index_page_name, expected_type=type_hints["spa_index_page_name"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "id": id,
                "path": path,
            }
            if spa_index_page_name is not None:
                self._values["spa_index_page_name"] = spa_index_page_name

        @builtins.property
        def id(self) -> builtins.str:
            '''(experimental) Unique identifier to delineate an asset from other assets.

            :stability: experimental
            '''
            result = self._values.get("id")
            assert result is not None, "Required property 'id' is missing"
            return typing.cast(builtins.str, result)

        @builtins.property
        def path(self) -> typing.Union[builtins.str, typing.List[builtins.str]]:
            '''(experimental) Path(s) on the local file system to the static asset(s).

            Each path must be either a directory or zip containing the assets

            :stability: experimental
            '''
            result = self._values.get("path")
            assert result is not None, "Required property 'path' is missing"
            return typing.cast(typing.Union[builtins.str, typing.List[builtins.str]], result)

        @builtins.property
        def spa_index_page_name(self) -> typing.Optional[builtins.str]:
            '''(experimental) Name of the index page for a Single Page Application (SPA).

            This is used as a default key to load when the path provided does not map to a concrete static asset.

            :stability: experimental

            Example::

                index.html
            '''
            result = self._values.get("spa_index_page_name")
            return typing.cast(typing.Optional[builtins.str], result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "Asset(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.CustomDomainConfiguration",
        jsii_struct_bases=[],
        name_mapping={"options": "options"},
    )
    class CustomDomainConfiguration:
        def __init__(
            self,
            *,
            options: typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]],
        ) -> None:
            '''(experimental) Domain configuration when using a Custom Domain Name for Amazon API Gateway.

            :param options: (experimental) Options for specifying the custom domain name setup.

            :stability: experimental
            '''
            if isinstance(options, dict):
                options = _aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions(**options)
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__fb7dd65e823631a881c3757f3933e65e12d0ec00138d9e332d7bffc3beddf9ee)
                check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "options": options,
            }

        @builtins.property
        def options(self) -> _aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions:
            '''(experimental) Options for specifying the custom domain name setup.

            :stability: experimental
            '''
            result = self._values.get("options")
            assert result is not None, "Required property 'options' is missing"
            return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "CustomDomainConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.DefaultEndpointConfiguration",
        jsii_struct_bases=[],
        name_mapping={"base_path": "basePath"},
    )
    class DefaultEndpointConfiguration:
        def __init__(self, *, base_path: builtins.str) -> None:
            '''(experimental) Domain configuration when using the Amazon API Gateway Default Execution Endpoint.

            :param base_path: (experimental) Base path where all assets will be located. This is because the default execution endpoint does not serve content at the root but off of a stage. As such this base path will be used to create the deployment stage to serve assets from.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__af579bdb0d2e5a9bf7625d102861181c02edc99e90f1bea8aad195fde82acc1f)
                check_type(argname="argument base_path", value=base_path, expected_type=type_hints["base_path"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "base_path": base_path,
            }

        @builtins.property
        def base_path(self) -> builtins.str:
            '''(experimental) Base path where all assets will be located.

            This is because the default execution endpoint does not serve content at the root but off of a stage. As
            such this base path will be used to create the deployment stage to serve assets from.

            :stability: experimental

            Example::

                /dev/site1
            '''
            result = self._values.get("base_path")
            assert result is not None, "Required property 'base_path' is missing"
            return typing.cast(builtins.str, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "DefaultEndpointConfiguration(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHosting.PatternComponents",
        jsii_struct_bases=[],
        name_mapping={
            "distribution": "distribution",
            "proxy": "proxy",
            "store": "store",
        },
    )
    class PatternComponents:
        def __init__(
            self,
            *,
            distribution: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
            proxy: _aws_cdk_aws_lambda_ceddda9d.Function,
            store: _aws_cdk_aws_s3_ceddda9d.Bucket,
        ) -> None:
            '''(experimental) Underlying components for the pattern.

            :param distribution: (experimental) Provides access to the underlying Amazon API Gateway REST API that serves as the distribution endpoint for the static content. WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not behave as expected or designed. You do so at your own risk.
            :param proxy: (experimental) Provides access to the underlying AWS Lambda function that proxies the static content from Amazon S3. WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not behave as expected or designed. You do so at your own risk.
            :param store: (experimental) Provides access to the underlying Amazon S3 bucket that stores the static content. WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            if __debug__:
                type_hints = typing.get_type_hints(_typecheckingstub__c61a977a949d583f93d83ff5cdd17e5856bd473ed360fd24f8219d952c9a0b61)
                check_type(argname="argument distribution", value=distribution, expected_type=type_hints["distribution"])
                check_type(argname="argument proxy", value=proxy, expected_type=type_hints["proxy"])
                check_type(argname="argument store", value=store, expected_type=type_hints["store"])
            self._values: typing.Dict[builtins.str, typing.Any] = {
                "distribution": distribution,
                "proxy": proxy,
                "store": store,
            }

        @builtins.property
        def distribution(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
            '''(experimental) Provides access to the underlying Amazon API Gateway REST API that serves as the distribution endpoint for the static content.

            WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
            behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            result = self._values.get("distribution")
            assert result is not None, "Required property 'distribution' is missing"
            return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, result)

        @builtins.property
        def proxy(self) -> _aws_cdk_aws_lambda_ceddda9d.Function:
            '''(experimental) Provides access to the underlying AWS Lambda function that proxies the static content from Amazon S3.

            WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
            behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            result = self._values.get("proxy")
            assert result is not None, "Required property 'proxy' is missing"
            return typing.cast(_aws_cdk_aws_lambda_ceddda9d.Function, result)

        @builtins.property
        def store(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
            '''(experimental) Provides access to the underlying Amazon S3 bucket that stores the static content.

            WARNING: Making changes to the properties of the underlying components of this pattern may cause it to not
            behave as expected or designed. You do so at your own risk.

            :stability: experimental
            '''
            result = self._values.get("store")
            assert result is not None, "Required property 'store' is missing"
            return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, result)

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "PatternComponents(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.ApiGatewayStaticHostingProps",
    jsii_struct_bases=[],
    name_mapping={
        "asset": "asset",
        "domain": "domain",
        "access_logging_bucket": "accessLoggingBucket",
        "access_policy": "accessPolicy",
        "api_log_destination": "apiLogDestination",
        "encryption": "encryption",
        "endpoint": "endpoint",
        "lambda_configuration": "lambdaConfiguration",
        "retain_store_on_deletion": "retainStoreOnDeletion",
        "version_tag": "versionTag",
    },
)
class ApiGatewayStaticHostingProps:
    def __init__(
        self,
        *,
        asset: typing.Union[ApiGatewayStaticHosting.Asset, typing.Dict[builtins.str, typing.Any]],
        domain: typing.Union[typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[ApiGatewayStaticHosting.DefaultEndpointConfiguration, typing.Dict[builtins.str, typing.Any]]],
        access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
        api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        retain_store_on_deletion: typing.Optional[builtins.bool] = None,
        version_tag: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Properties for configuring the static hosting pattern.

        :param asset: (experimental) Metadata about the static assets to host.
        :param domain: (experimental) Configuration information for the distribution endpoint that will be used to serve static content.
        :param access_logging_bucket: (experimental) Amazon S3 bucket where access logs should be stored. Default: undefined A new bucket will be created for storing access logs
        :param access_policy: (experimental) Resource access policy to define on the API itself to control who can invoke the endpoint.
        :param api_log_destination: (experimental) Destination where Amazon API Gateway logs can be sent.
        :param encryption: (experimental) Encryption key for protecting the framework resources. Default: undefined AWS service-managed encryption keys will be used where available
        :param endpoint: (experimental) Endpoint deployment information for the REST API. Default: undefined Will deploy an edge-optimized API
        :param lambda_configuration: (experimental) Optional configuration settings for the backend handler.
        :param retain_store_on_deletion: (experimental) Whether or not to retain the Amazon S3 bucket where static assets are deployed on stack deletion. Default: false The Amazon S3 bucket and all assets contained within will be deleted
        :param version_tag: (experimental) A version identifier to deploy to the Amazon S3 bucket to help with rapid identification of current deployment This will appear as ``metadata.json`` at the root of the bucket. Default: undefined No version information will be deployed to the Amazon S3 bucket

        :stability: experimental
        '''
        if isinstance(asset, dict):
            asset = ApiGatewayStaticHosting.Asset(**asset)
        if isinstance(endpoint, dict):
            endpoint = _aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration(**endpoint)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4baf4c2294bf49627829b500b5815750efb5085b8be745e95cfca95c61678fd6)
            check_type(argname="argument asset", value=asset, expected_type=type_hints["asset"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument access_logging_bucket", value=access_logging_bucket, expected_type=type_hints["access_logging_bucket"])
            check_type(argname="argument access_policy", value=access_policy, expected_type=type_hints["access_policy"])
            check_type(argname="argument api_log_destination", value=api_log_destination, expected_type=type_hints["api_log_destination"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument retain_store_on_deletion", value=retain_store_on_deletion, expected_type=type_hints["retain_store_on_deletion"])
            check_type(argname="argument version_tag", value=version_tag, expected_type=type_hints["version_tag"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "asset": asset,
            "domain": domain,
        }
        if access_logging_bucket is not None:
            self._values["access_logging_bucket"] = access_logging_bucket
        if access_policy is not None:
            self._values["access_policy"] = access_policy
        if api_log_destination is not None:
            self._values["api_log_destination"] = api_log_destination
        if encryption is not None:
            self._values["encryption"] = encryption
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if retain_store_on_deletion is not None:
            self._values["retain_store_on_deletion"] = retain_store_on_deletion
        if version_tag is not None:
            self._values["version_tag"] = version_tag

    @builtins.property
    def asset(self) -> ApiGatewayStaticHosting.Asset:
        '''(experimental) Metadata about the static assets to host.

        :stability: experimental
        '''
        result = self._values.get("asset")
        assert result is not None, "Required property 'asset' is missing"
        return typing.cast(ApiGatewayStaticHosting.Asset, result)

    @builtins.property
    def domain(
        self,
    ) -> typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, ApiGatewayStaticHosting.DefaultEndpointConfiguration]:
        '''(experimental) Configuration information for the distribution endpoint that will be used to serve static content.

        :stability: experimental
        '''
        result = self._values.get("domain")
        assert result is not None, "Required property 'domain' is missing"
        return typing.cast(typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, ApiGatewayStaticHosting.DefaultEndpointConfiguration], result)

    @builtins.property
    def access_logging_bucket(
        self,
    ) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket]:
        '''(experimental) Amazon S3 bucket where access logs should be stored.

        :default: undefined A new bucket will be created for storing access logs

        :stability: experimental
        '''
        result = self._values.get("access_logging_bucket")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket], result)

    @builtins.property
    def access_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) Resource access policy to define on the API itself to control who can invoke the endpoint.

        :stability: experimental
        '''
        result = self._values.get("access_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    @builtins.property
    def api_log_destination(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination]:
        '''(experimental) Destination where Amazon API Gateway logs can be sent.

        :stability: experimental
        '''
        result = self._values.get("api_log_destination")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Encryption key for protecting the framework resources.

        :default: undefined AWS service-managed encryption keys will be used where available

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration]:
        '''(experimental) Endpoint deployment information for the REST API.

        :default: undefined Will deploy an edge-optimized API

        :stability: experimental
        '''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional configuration settings for the backend handler.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def retain_store_on_deletion(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether or not to retain the Amazon S3 bucket where static assets are deployed on stack deletion.

        :default: false The Amazon S3 bucket and all assets contained within will be deleted

        :stability: experimental
        '''
        result = self._values.get("retain_store_on_deletion")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def version_tag(self) -> typing.Optional[builtins.str]:
        '''(experimental) A version identifier to deploy to the Amazon S3 bucket to help with rapid identification of current deployment This will appear as ``metadata.json`` at the root of the bucket.

        :default: undefined No version information will be deployed to the Amazon S3 bucket

        :stability: experimental

        Example::

            1.0.2
        '''
        result = self._values.get("version_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiGatewayStaticHostingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Ec2LinuxImagePipeline(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipeline",
):
    '''(experimental) A pattern to build an EC2 Image Pipeline specifically for Linux.

    This pattern contains opinionated code and features to help create a linux
    pipeline. This pattern further simplifies setting up an image pipeline by
    letting you choose specific operating systems and features. In addition, this
    pattern will automatically start the pipeline and wait for it to complete.
    This allows you to reference the AMI from this construct and utilize it in
    your application (see example).

    The example below shows how you can configure an image that contains the AWS
    CLI and retains the SSM agent on the image. The image will have a 100GB root
    volume.

    :stability: experimental

    Example::

        import { CfnOutput } from 'aws-cdk-lib';
        import { Ec2LinuxImagePipeline } from '@cdklabs/cdk-proserve-lib/patterns';
        
        const pipeline = new Ec2LinuxImagePipeline(this, 'ImagePipeline', {
          version: '0.1.0',
          operatingSystem:
            Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023,
          rootVolumeSize: 100,
          features: [
            Ec2LinuxImagePipeline.Feature.AWS_CLI,
            Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT
          ]
        );
        
        new CfnOutput(this, 'AmiId', {
          value: pipeline.latestAmi,
        })
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
        extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        features: typing.Optional[typing.Sequence["Ec2LinuxImagePipeline.Feature"]] = None,
        operating_system: typing.Optional["Ec2LinuxImagePipeline.OperatingSystem"] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
        version: builtins.str,
        build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) A pattern to build an EC2 Image Pipeline specifically for Linux.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID.
        :param extra_components: (experimental) Additional components to install in the image. These components will be added after the default Linux components. Use this to add custom components beyond the predefined features.
        :param extra_device_mappings: (experimental) Additional EBS volume mappings to add to the image. These volumes will be added in addition to the root volume. Use this to specify additional storage volumes that should be included in the AMI.
        :param features: (experimental) A list of features to install on the image. Features are predefined sets of components and configurations. Default: [AWS_CLI, RETAIN_SSM_AGENT] Default: [Ec2LinuxImagePipeline.Feature.AWS_CLI, Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT]
        :param operating_system: (experimental) The operating system to use for the image pipeline. Specifies which operating system version to use as the base image. Default: AMAZON_LINUX_2023. Default: Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023
        :param root_volume_size: (experimental) Size for the root volume in GB. Default: 10 GB. Default: 10
        :param version: (experimental) Version of the image pipeline. This must be updated if you make underlying changes to the pipeline configuration.
        :param build_configuration: (experimental) Configuration options for the build process.
        :param description: (experimental) Description of the image pipeline.
        :param encryption: (experimental) KMS key for encryption.
        :param instance_types: (experimental) Instance types for the Image Builder Pipeline. Default: [t3.medium]
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param vpc_configuration: (experimental) VPC configuration for the image pipeline.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfe75b8964707df740912e083b8358a4e940f27f7259ab820504b6c2ada0e612)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = Ec2LinuxImagePipelineProps(
            extra_components=extra_components,
            extra_device_mappings=extra_device_mappings,
            features=features,
            operating_system=operating_system,
            root_volume_size=root_volume_size,
            version=version,
            build_configuration=build_configuration,
            description=description,
            encryption=encryption,
            instance_types=instance_types,
            lambda_configuration=lambda_configuration,
            vpc_configuration=vpc_configuration,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="imagePipelineArn")
    def image_pipeline_arn(self) -> builtins.str:
        '''(experimental) The Amazon Resource Name (ARN) of the Image Pipeline.

        Used to uniquely identify this image pipeline.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "imagePipelineArn"))

    @image_pipeline_arn.setter
    def image_pipeline_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__480b8d9ad288b00a9019dff6ab448fa0084409e75666e22ebc710de08d511ef1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePipelineArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="imagePipelineTopic")
    def image_pipeline_topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        '''(experimental) The SNS Topic associated with this Image Pipeline.

        Publishes notifications about pipeline execution events.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "imagePipelineTopic"))

    @image_pipeline_topic.setter
    def image_pipeline_topic(self, value: _aws_cdk_aws_sns_ceddda9d.ITopic) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50c054b2b518ad1fdc972c31ac61f4ccead58620ac1a7b23a125009d747bc370)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePipelineTopic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="latestAmi")
    def latest_ami(self) -> typing.Optional[builtins.str]:
        '''(experimental) The latest AMI built by the pipeline.

        NOTE: You must have enabled the
        Build Configuration option to wait for image build completion for this
        property to be available.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "latestAmi"))

    @latest_ami.setter
    def latest_ami(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e396117a6c4ae570f398094ede114baa7576df8e02406727ef327dda84877bda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "latestAmi", value) # pyright: ignore[reportArgumentType]

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipeline.Feature"
    )
    class Feature(enum.Enum):
        '''
        :stability: experimental
        '''

        AWS_CLI = "AWS_CLI"
        '''
        :stability: experimental
        '''
        NICE_DCV = "NICE_DCV"
        '''
        :stability: experimental
        '''
        RETAIN_SSM_AGENT = "RETAIN_SSM_AGENT"
        '''
        :stability: experimental
        '''
        STIG = "STIG"
        '''
        :stability: experimental
        '''
        SCAP = "SCAP"
        '''
        :stability: experimental
        '''

    @jsii.enum(
        jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipeline.OperatingSystem"
    )
    class OperatingSystem(enum.Enum):
        '''
        :stability: experimental
        '''

        RED_HAT_ENTERPRISE_LINUX_8_9 = "RED_HAT_ENTERPRISE_LINUX_8_9"
        '''
        :stability: experimental
        '''
        AMAZON_LINUX_2 = "AMAZON_LINUX_2"
        '''
        :stability: experimental
        '''
        AMAZON_LINUX_2023 = "AMAZON_LINUX_2023"
        '''
        :stability: experimental
        '''


@jsii.data_type(
    jsii_type="@cdklabs/cdk-proserve-lib.patterns.Ec2LinuxImagePipelineProps",
    jsii_struct_bases=[_Ec2ImagePipelineBaseProps_b9c7b595],
    name_mapping={
        "version": "version",
        "build_configuration": "buildConfiguration",
        "description": "description",
        "encryption": "encryption",
        "instance_types": "instanceTypes",
        "lambda_configuration": "lambdaConfiguration",
        "vpc_configuration": "vpcConfiguration",
        "extra_components": "extraComponents",
        "extra_device_mappings": "extraDeviceMappings",
        "features": "features",
        "operating_system": "operatingSystem",
        "root_volume_size": "rootVolumeSize",
    },
)
class Ec2LinuxImagePipelineProps(_Ec2ImagePipelineBaseProps_b9c7b595):
    def __init__(
        self,
        *,
        version: builtins.str,
        build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
        vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
        extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
        extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        features: typing.Optional[typing.Sequence[Ec2LinuxImagePipeline.Feature]] = None,
        operating_system: typing.Optional[Ec2LinuxImagePipeline.OperatingSystem] = None,
        root_volume_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Properties for creating a Linux STIG Image Pipeline.

        :param version: (experimental) Version of the image pipeline. This must be updated if you make underlying changes to the pipeline configuration.
        :param build_configuration: (experimental) Configuration options for the build process.
        :param description: (experimental) Description of the image pipeline.
        :param encryption: (experimental) KMS key for encryption.
        :param instance_types: (experimental) Instance types for the Image Builder Pipeline. Default: [t3.medium]
        :param lambda_configuration: (experimental) Optional Lambda configuration settings.
        :param vpc_configuration: (experimental) VPC configuration for the image pipeline.
        :param extra_components: (experimental) Additional components to install in the image. These components will be added after the default Linux components. Use this to add custom components beyond the predefined features.
        :param extra_device_mappings: (experimental) Additional EBS volume mappings to add to the image. These volumes will be added in addition to the root volume. Use this to specify additional storage volumes that should be included in the AMI.
        :param features: (experimental) A list of features to install on the image. Features are predefined sets of components and configurations. Default: [AWS_CLI, RETAIN_SSM_AGENT] Default: [Ec2LinuxImagePipeline.Feature.AWS_CLI, Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT]
        :param operating_system: (experimental) The operating system to use for the image pipeline. Specifies which operating system version to use as the base image. Default: AMAZON_LINUX_2023. Default: Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023
        :param root_volume_size: (experimental) Size for the root volume in GB. Default: 10 GB. Default: 10

        :stability: experimental
        '''
        if isinstance(build_configuration, dict):
            build_configuration = _Ec2ImagePipeline_08b5ca60.BuildConfigurationProps(**build_configuration)
        if isinstance(lambda_configuration, dict):
            lambda_configuration = _LambdaConfiguration_9f8afc24(**lambda_configuration)
        if isinstance(vpc_configuration, dict):
            vpc_configuration = _Ec2ImagePipeline_08b5ca60.VpcConfigurationProps(**vpc_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d272e504a6fabc4b04d50467e7c5293e2777ed064ddb4c6626d553e16c42dd65)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument build_configuration", value=build_configuration, expected_type=type_hints["build_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument instance_types", value=instance_types, expected_type=type_hints["instance_types"])
            check_type(argname="argument lambda_configuration", value=lambda_configuration, expected_type=type_hints["lambda_configuration"])
            check_type(argname="argument vpc_configuration", value=vpc_configuration, expected_type=type_hints["vpc_configuration"])
            check_type(argname="argument extra_components", value=extra_components, expected_type=type_hints["extra_components"])
            check_type(argname="argument extra_device_mappings", value=extra_device_mappings, expected_type=type_hints["extra_device_mappings"])
            check_type(argname="argument features", value=features, expected_type=type_hints["features"])
            check_type(argname="argument operating_system", value=operating_system, expected_type=type_hints["operating_system"])
            check_type(argname="argument root_volume_size", value=root_volume_size, expected_type=type_hints["root_volume_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
        }
        if build_configuration is not None:
            self._values["build_configuration"] = build_configuration
        if description is not None:
            self._values["description"] = description
        if encryption is not None:
            self._values["encryption"] = encryption
        if instance_types is not None:
            self._values["instance_types"] = instance_types
        if lambda_configuration is not None:
            self._values["lambda_configuration"] = lambda_configuration
        if vpc_configuration is not None:
            self._values["vpc_configuration"] = vpc_configuration
        if extra_components is not None:
            self._values["extra_components"] = extra_components
        if extra_device_mappings is not None:
            self._values["extra_device_mappings"] = extra_device_mappings
        if features is not None:
            self._values["features"] = features
        if operating_system is not None:
            self._values["operating_system"] = operating_system
        if root_volume_size is not None:
            self._values["root_volume_size"] = root_volume_size

    @builtins.property
    def version(self) -> builtins.str:
        '''(experimental) Version of the image pipeline.

        This must be updated if you make
        underlying changes to the pipeline configuration.

        :stability: experimental
        '''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_configuration(
        self,
    ) -> typing.Optional[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps]:
        '''(experimental) Configuration options for the build process.

        :stability: experimental
        '''
        result = self._values.get("build_configuration")
        return typing.cast(typing.Optional[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description of the image pipeline.

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) KMS key for encryption.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def instance_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) Instance types for the Image Builder Pipeline.

        Default: [t3.medium]

        :stability: experimental
        '''
        result = self._values.get("instance_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def lambda_configuration(self) -> typing.Optional[_LambdaConfiguration_9f8afc24]:
        '''(experimental) Optional Lambda configuration settings.

        :stability: experimental
        '''
        result = self._values.get("lambda_configuration")
        return typing.cast(typing.Optional[_LambdaConfiguration_9f8afc24], result)

    @builtins.property
    def vpc_configuration(
        self,
    ) -> typing.Optional[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps]:
        '''(experimental) VPC configuration for the image pipeline.

        :stability: experimental
        '''
        result = self._values.get("vpc_configuration")
        return typing.cast(typing.Optional[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps], result)

    @builtins.property
    def extra_components(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]]:
        '''(experimental) Additional components to install in the image.

        These components will be added after the default Linux components.
        Use this to add custom components beyond the predefined features.

        :stability: experimental
        '''
        result = self._values.get("extra_components")
        return typing.cast(typing.Optional[typing.List[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]], result)

    @builtins.property
    def extra_device_mappings(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty]]:
        '''(experimental) Additional EBS volume mappings to add to the image.

        These volumes will be added in addition to the root volume.
        Use this to specify additional storage volumes that should be included in the AMI.

        :stability: experimental
        '''
        result = self._values.get("extra_device_mappings")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty]], result)

    @builtins.property
    def features(self) -> typing.Optional[typing.List[Ec2LinuxImagePipeline.Feature]]:
        '''(experimental) A list of features to install on the image.

        Features are predefined sets of components and configurations.
        Default: [AWS_CLI, RETAIN_SSM_AGENT]

        :default: [Ec2LinuxImagePipeline.Feature.AWS_CLI, Ec2LinuxImagePipeline.Feature.RETAIN_SSM_AGENT]

        :stability: experimental
        '''
        result = self._values.get("features")
        return typing.cast(typing.Optional[typing.List[Ec2LinuxImagePipeline.Feature]], result)

    @builtins.property
    def operating_system(
        self,
    ) -> typing.Optional[Ec2LinuxImagePipeline.OperatingSystem]:
        '''(experimental) The operating system to use for the image pipeline.

        Specifies which operating system version to use as the base image.
        Default: AMAZON_LINUX_2023.

        :default: Ec2LinuxImagePipeline.OperatingSystem.AMAZON_LINUX_2023

        :stability: experimental
        '''
        result = self._values.get("operating_system")
        return typing.cast(typing.Optional[Ec2LinuxImagePipeline.OperatingSystem], result)

    @builtins.property
    def root_volume_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Size for the root volume in GB.

        Default: 10 GB.

        :default: 10

        :stability: experimental
        '''
        result = self._values.get("root_volume_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Ec2LinuxImagePipelineProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApiGatewayStaticHosting",
    "ApiGatewayStaticHostingProps",
    "Ec2LinuxImagePipeline",
    "Ec2LinuxImagePipelineProps",
]

publication.publish()

def _typecheckingstub__926e3ab1cdccdb34f4dc75a68890781e04a583c1ec8481b471267ea1ecbb3c22(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    asset: typing.Union[ApiGatewayStaticHosting.Asset, typing.Dict[builtins.str, typing.Any]],
    domain: typing.Union[typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[ApiGatewayStaticHosting.DefaultEndpointConfiguration, typing.Dict[builtins.str, typing.Any]]],
    access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    retain_store_on_deletion: typing.Optional[builtins.bool] = None,
    version_tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95377bd339103860abda9142b547350593c2c75dc36900d1cafdbd3ed1452918(
    *,
    id: builtins.str,
    path: typing.Union[builtins.str, typing.Sequence[builtins.str]],
    spa_index_page_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb7dd65e823631a881c3757f3933e65e12d0ec00138d9e332d7bffc3beddf9ee(
    *,
    options: typing.Union[_aws_cdk_aws_apigateway_ceddda9d.DomainNameOptions, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af579bdb0d2e5a9bf7625d102861181c02edc99e90f1bea8aad195fde82acc1f(
    *,
    base_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61a977a949d583f93d83ff5cdd17e5856bd473ed360fd24f8219d952c9a0b61(
    *,
    distribution: _aws_cdk_aws_apigateway_ceddda9d.RestApi,
    proxy: _aws_cdk_aws_lambda_ceddda9d.Function,
    store: _aws_cdk_aws_s3_ceddda9d.Bucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4baf4c2294bf49627829b500b5815750efb5085b8be745e95cfca95c61678fd6(
    *,
    asset: typing.Union[ApiGatewayStaticHosting.Asset, typing.Dict[builtins.str, typing.Any]],
    domain: typing.Union[typing.Union[ApiGatewayStaticHosting.CustomDomainConfiguration, typing.Dict[builtins.str, typing.Any]], typing.Union[ApiGatewayStaticHosting.DefaultEndpointConfiguration, typing.Dict[builtins.str, typing.Any]]],
    access_logging_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    access_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    api_log_destination: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAccessLogDestination] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    endpoint: typing.Optional[typing.Union[_aws_cdk_aws_apigateway_ceddda9d.EndpointConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    retain_store_on_deletion: typing.Optional[builtins.bool] = None,
    version_tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfe75b8964707df740912e083b8358a4e940f27f7259ab820504b6c2ada0e612(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
    extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    features: typing.Optional[typing.Sequence[Ec2LinuxImagePipeline.Feature]] = None,
    operating_system: typing.Optional[Ec2LinuxImagePipeline.OperatingSystem] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
    version: builtins.str,
    build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__480b8d9ad288b00a9019dff6ab448fa0084409e75666e22ebc710de08d511ef1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50c054b2b518ad1fdc972c31ac61f4ccead58620ac1a7b23a125009d747bc370(
    value: _aws_cdk_aws_sns_ceddda9d.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e396117a6c4ae570f398094ede114baa7576df8e02406727ef327dda84877bda(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d272e504a6fabc4b04d50467e7c5293e2777ed064ddb4c6626d553e16c42dd65(
    *,
    version: builtins.str,
    build_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.BuildConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    instance_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    lambda_configuration: typing.Optional[typing.Union[_LambdaConfiguration_9f8afc24, typing.Dict[builtins.str, typing.Any]]] = None,
    vpc_configuration: typing.Optional[typing.Union[_Ec2ImagePipeline_08b5ca60.VpcConfigurationProps, typing.Dict[builtins.str, typing.Any]]] = None,
    extra_components: typing.Optional[typing.Sequence[typing.Union[_Ec2ImagePipeline_08b5ca60.Component, _aws_cdk_aws_imagebuilder_ceddda9d.CfnComponent]]] = None,
    extra_device_mappings: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_imagebuilder_ceddda9d.CfnImageRecipe.InstanceBlockDeviceMappingProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
    features: typing.Optional[typing.Sequence[Ec2LinuxImagePipeline.Feature]] = None,
    operating_system: typing.Optional[Ec2LinuxImagePipeline.OperatingSystem] = None,
    root_volume_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
