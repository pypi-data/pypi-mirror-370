r'''
# cloudstructs

High-level constructs for AWS CDK

## Installation

`npm install cloudstructs` or `yarn add cloudstructs`

Version >= 0.2.0 requires AWS CDK v2.

## Constructs

* [`CodeCommitMirror`](src/codecommit-mirror) Mirror a repository to AWS CodeCommit on schedule
* [`EcsServiceRoller`](src/ecs-service-roller) Roll your ECS service tasks on schedule or with
  a rule
* [`EmailReceiver`](src/email-receiver) Receive emails through SES, save them to S3
  and invoke a Lambda function
* [`MjmlTemplate`](src/mjml-template) SES email template from [MJML](https://mjml.io/)
* [`SlackApp`](src/slack-app) Deploy Slack apps from manifests
* [`SlackEvents`](src/slack-events) Send Slack events to Amazon EventBridge
* [`SlackTextract`](src/slack-textract) Extract text from images posted to Slack
  using Amazon Textract. The extracted text is posted in a thread under the image
  and gets indexed!
* [`SslServerTest`](src/ssl-server-test) Test a server/host for SSL/TLS on schedule and
  get notified when the overall rating is not satisfactory. [Powered by Qualys SSL Labs](https://www.ssllabs.com/).
* [`StateMachineCustomResourceProvider`](src/state-machine-cr-provider) Implement custom
  resources with AWS Step Functions state machines
* [`StaticWebsite`](src/static-website) A CloudFront static website hosted on S3 with
  HTTPS redirect, SPA redirect, HTTP security headers and backend configuration saved
  to the bucket.
* [`ToolkitCleaner`](src/toolkit-cleaner) Clean unused S3 and ECR assets from your CDK
  Toolkit.
* [`UrlShortener`](src/url-shortener) Deploy an URL shortener API
'''
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

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_apigateway as _aws_cdk_aws_apigateway_ceddda9d
import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import aws_cdk.aws_ses as _aws_cdk_aws_ses_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


class CodeCommitMirror(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.CodeCommitMirror",
):
    '''Mirror a repository to AWS CodeCommit on schedule.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        repository: "CodeCommitMirrorSourceRepository",
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: The ECS cluster where to run the mirroring operation.
        :param repository: The source repository.
        :param schedule: The schedule for the mirroring operation. Default: - everyday at midnight
        :param subnet_selection: Where to run the mirroring Fargate tasks. Default: - public subnets
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__775d0a2a4ad4d1672c6555b5fea4da6dc7435ddea6c63db13b79d587651e13c1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeCommitMirrorProps(
            cluster=cluster,
            repository=repository,
            schedule=schedule,
            subnet_selection=subnet_selection,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.CodeCommitMirrorProps",
    jsii_struct_bases=[],
    name_mapping={
        "cluster": "cluster",
        "repository": "repository",
        "schedule": "schedule",
        "subnet_selection": "subnetSelection",
    },
)
class CodeCommitMirrorProps:
    def __init__(
        self,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        repository: "CodeCommitMirrorSourceRepository",
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Properties for a CodeCommitMirror.

        :param cluster: The ECS cluster where to run the mirroring operation.
        :param repository: The source repository.
        :param schedule: The schedule for the mirroring operation. Default: - everyday at midnight
        :param subnet_selection: Where to run the mirroring Fargate tasks. Default: - public subnets
        '''
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea93461a0d56e64ddfee27f76a8f585e8ab317fa994825218d03706d0684ec6b)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "repository": repository,
        }
        if schedule is not None:
            self._values["schedule"] = schedule
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''The ECS cluster where to run the mirroring operation.'''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, result)

    @builtins.property
    def repository(self) -> "CodeCommitMirrorSourceRepository":
        '''The source repository.'''
        result = self._values.get("repository")
        assert result is not None, "Required property 'repository' is missing"
        return typing.cast("CodeCommitMirrorSourceRepository", result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The schedule for the mirroring operation.

        :default: - everyday at midnight
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''Where to run the mirroring Fargate tasks.

        :default: - public subnets
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeCommitMirrorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CodeCommitMirrorSourceRepository(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cloudstructs.CodeCommitMirrorSourceRepository",
):
    '''A source repository for AWS CodeCommit mirroring.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="gitHub")
    @builtins.classmethod
    def git_hub(
        cls,
        owner: builtins.str,
        name: builtins.str,
    ) -> "CodeCommitMirrorSourceRepository":
        '''Public GitHub repository.

        :param owner: -
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09f67e4d4aeae1f0358e343cd060bc1a176ef8adf4a4b5c49a3b8216aa4f0c5b)
            check_type(argname="argument owner", value=owner, expected_type=type_hints["owner"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("CodeCommitMirrorSourceRepository", jsii.sinvoke(cls, "gitHub", [owner, name]))

    @jsii.member(jsii_name="private")
    @builtins.classmethod
    def private(
        cls,
        name: builtins.str,
        url: _aws_cdk_aws_ecs_ceddda9d.Secret,
    ) -> "CodeCommitMirrorSourceRepository":
        '''Private repository with HTTPS clone URL stored in a AWS Secrets Manager secret or a AWS Systems Manager secure string parameter.

        :param name: the repository name.
        :param url: the secret containing the HTTPS clone URL.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9c5ea96c99b4d98cccb560282863340d507a7bea06dd48c633374937c378a51)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        return typing.cast("CodeCommitMirrorSourceRepository", jsii.sinvoke(cls, "private", [name, url]))

    @builtins.property
    @jsii.member(jsii_name="name")
    @abc.abstractmethod
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="plainTextUrl")
    @abc.abstractmethod
    def plain_text_url(self) -> typing.Optional[builtins.str]:
        '''The HTTPS clone URL in plain text, used for a public repository.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="secretUrl")
    @abc.abstractmethod
    def secret_url(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Secret]:
        '''The HTTPS clone URL if the repository is private.

        The secret should contain the username and/or token.

        Example::

            `https://TOKEN@github.com/owner/name`
            `https://USERNAME:TOKEN@bitbucket.org/owner/name.git`
        '''
        ...


class _CodeCommitMirrorSourceRepositoryProxy(CodeCommitMirrorSourceRepository):
    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''The name of the repository.'''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="plainTextUrl")
    def plain_text_url(self) -> typing.Optional[builtins.str]:
        '''The HTTPS clone URL in plain text, used for a public repository.'''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "plainTextUrl"))

    @builtins.property
    @jsii.member(jsii_name="secretUrl")
    def secret_url(self) -> typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Secret]:
        '''The HTTPS clone URL if the repository is private.

        The secret should contain the username and/or token.

        Example::

            `https://TOKEN@github.com/owner/name`
            `https://USERNAME:TOKEN@bitbucket.org/owner/name.git`
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ecs_ceddda9d.Secret], jsii.get(self, "secretUrl"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, CodeCommitMirrorSourceRepository).__jsii_proxy_class__ = lambda : _CodeCommitMirrorSourceRepositoryProxy


@jsii.enum(jsii_type="cloudstructs.DmarcAlignment")
class DmarcAlignment(enum.Enum):
    '''The DMARC alignment mode.'''

    RELAXED = "RELAXED"
    '''Relaxed alignment mode.'''
    STRICT = "STRICT"
    '''Strict alignment mode.'''


@jsii.enum(jsii_type="cloudstructs.DmarcPolicy")
class DmarcPolicy(enum.Enum):
    '''The DMARC policy to apply to messages that fail DMARC compliance.'''

    NONE = "NONE"
    '''Do not apply any special handling to messages that fail DMARC compliance.'''
    QUARANTINE = "QUARANTINE"
    '''Quarantine messages that fail DMARC compliance.

    (usually by sending them to spam)
    '''
    REJECT = "REJECT"
    '''Reject messages that fail DMARC compliance.

    (usually by rejecting them outright)
    '''


class DmarcReporter(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.DmarcReporter",
):
    '''Creates a DMARC record in Route 53 and invokes a Lambda function to process incoming reports.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        dmarc_policy: DmarcPolicy,
        function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
        additional_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
        dmarc_dkim_alignment: typing.Optional[DmarcAlignment] = None,
        dmarc_percentage: typing.Optional[jsii.Number] = None,
        dmarc_spf_alignment: typing.Optional[DmarcAlignment] = None,
        dmarc_subdomain_policy: typing.Optional[DmarcPolicy] = None,
        email_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param dmarc_policy: The DMARC policy to apply to messages that fail DMARC compliance. This can be one of the following values: - none: Do not apply any special handling to messages that fail DMARC compliance. - quarantine: Quarantine messages that fail DMARC compliance. - reject: Reject messages that fail DMARC compliance.
        :param function: A Lambda function to invoke after the message is saved to S3. The Lambda function will be invoked with a SESMessage as event.
        :param hosted_zone: The Route 53 hosted zone to create the DMARC record in.
        :param receipt_rule_set: The SES receipt rule set where a receipt rule will be added.
        :param additional_email_addresses: Additional email addresses to send DMARC reports to.
        :param after_rule: An existing rule after which the new rule will be placed in the rule set. Default: - The new rule is inserted at the beginning of the rule list.
        :param dmarc_dkim_alignment: The alignment mode to use for DKIM signatures. This can be one of the following values: - relaxed: Use relaxed alignment mode. - strict: Use strict alignment mode. Default: relaxed
        :param dmarc_percentage: The percentage of messages that should be checked for DMARC compliance. This is a value between 0 and 100. Default: 100
        :param dmarc_spf_alignment: The alignment mode to use for SPF signatures. This can be one of the following values: - relaxed: Use relaxed alignment mode. - strict: Use strict alignment mode. Default: relaxed
        :param dmarc_subdomain_policy: The DMARC policy to apply to messages that fail DMARC compliance for subdomains. This can be one of the following values: - none: Do not apply any special handling to messages that fail DMARC compliance. - quarantine: Quarantine messages that fail DMARC compliance. - reject: Reject messages that fail DMARC compliance. Default: inherited from dmarcPolicy
        :param email_address: The email address to send DMARC reports to. This email address must be verified in SES. Default: dmarc-reports@${hostedZone.zoneName}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01bd02e34cc162be822e89501c85ac44ba576832ec13dfbe18c7d3f48c6caa7f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = DmarcReporterProps(
            dmarc_policy=dmarc_policy,
            function=function,
            hosted_zone=hosted_zone,
            receipt_rule_set=receipt_rule_set,
            additional_email_addresses=additional_email_addresses,
            after_rule=after_rule,
            dmarc_dkim_alignment=dmarc_dkim_alignment,
            dmarc_percentage=dmarc_percentage,
            dmarc_spf_alignment=dmarc_spf_alignment,
            dmarc_subdomain_policy=dmarc_subdomain_policy,
            email_address=email_address,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.DmarcReporterProps",
    jsii_struct_bases=[],
    name_mapping={
        "dmarc_policy": "dmarcPolicy",
        "function": "function",
        "hosted_zone": "hostedZone",
        "receipt_rule_set": "receiptRuleSet",
        "additional_email_addresses": "additionalEmailAddresses",
        "after_rule": "afterRule",
        "dmarc_dkim_alignment": "dmarcDkimAlignment",
        "dmarc_percentage": "dmarcPercentage",
        "dmarc_spf_alignment": "dmarcSpfAlignment",
        "dmarc_subdomain_policy": "dmarcSubdomainPolicy",
        "email_address": "emailAddress",
    },
)
class DmarcReporterProps:
    def __init__(
        self,
        *,
        dmarc_policy: DmarcPolicy,
        function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
        additional_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
        dmarc_dkim_alignment: typing.Optional[DmarcAlignment] = None,
        dmarc_percentage: typing.Optional[jsii.Number] = None,
        dmarc_spf_alignment: typing.Optional[DmarcAlignment] = None,
        dmarc_subdomain_policy: typing.Optional[DmarcPolicy] = None,
        email_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for a DmarcReporter.

        :param dmarc_policy: The DMARC policy to apply to messages that fail DMARC compliance. This can be one of the following values: - none: Do not apply any special handling to messages that fail DMARC compliance. - quarantine: Quarantine messages that fail DMARC compliance. - reject: Reject messages that fail DMARC compliance.
        :param function: A Lambda function to invoke after the message is saved to S3. The Lambda function will be invoked with a SESMessage as event.
        :param hosted_zone: The Route 53 hosted zone to create the DMARC record in.
        :param receipt_rule_set: The SES receipt rule set where a receipt rule will be added.
        :param additional_email_addresses: Additional email addresses to send DMARC reports to.
        :param after_rule: An existing rule after which the new rule will be placed in the rule set. Default: - The new rule is inserted at the beginning of the rule list.
        :param dmarc_dkim_alignment: The alignment mode to use for DKIM signatures. This can be one of the following values: - relaxed: Use relaxed alignment mode. - strict: Use strict alignment mode. Default: relaxed
        :param dmarc_percentage: The percentage of messages that should be checked for DMARC compliance. This is a value between 0 and 100. Default: 100
        :param dmarc_spf_alignment: The alignment mode to use for SPF signatures. This can be one of the following values: - relaxed: Use relaxed alignment mode. - strict: Use strict alignment mode. Default: relaxed
        :param dmarc_subdomain_policy: The DMARC policy to apply to messages that fail DMARC compliance for subdomains. This can be one of the following values: - none: Do not apply any special handling to messages that fail DMARC compliance. - quarantine: Quarantine messages that fail DMARC compliance. - reject: Reject messages that fail DMARC compliance. Default: inherited from dmarcPolicy
        :param email_address: The email address to send DMARC reports to. This email address must be verified in SES. Default: dmarc-reports@${hostedZone.zoneName}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8808781a101fae34a67aa2c6db024d6ac63f2f0c2584452a348244b8a7c0b728)
            check_type(argname="argument dmarc_policy", value=dmarc_policy, expected_type=type_hints["dmarc_policy"])
            check_type(argname="argument function", value=function, expected_type=type_hints["function"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument receipt_rule_set", value=receipt_rule_set, expected_type=type_hints["receipt_rule_set"])
            check_type(argname="argument additional_email_addresses", value=additional_email_addresses, expected_type=type_hints["additional_email_addresses"])
            check_type(argname="argument after_rule", value=after_rule, expected_type=type_hints["after_rule"])
            check_type(argname="argument dmarc_dkim_alignment", value=dmarc_dkim_alignment, expected_type=type_hints["dmarc_dkim_alignment"])
            check_type(argname="argument dmarc_percentage", value=dmarc_percentage, expected_type=type_hints["dmarc_percentage"])
            check_type(argname="argument dmarc_spf_alignment", value=dmarc_spf_alignment, expected_type=type_hints["dmarc_spf_alignment"])
            check_type(argname="argument dmarc_subdomain_policy", value=dmarc_subdomain_policy, expected_type=type_hints["dmarc_subdomain_policy"])
            check_type(argname="argument email_address", value=email_address, expected_type=type_hints["email_address"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dmarc_policy": dmarc_policy,
            "function": function,
            "hosted_zone": hosted_zone,
            "receipt_rule_set": receipt_rule_set,
        }
        if additional_email_addresses is not None:
            self._values["additional_email_addresses"] = additional_email_addresses
        if after_rule is not None:
            self._values["after_rule"] = after_rule
        if dmarc_dkim_alignment is not None:
            self._values["dmarc_dkim_alignment"] = dmarc_dkim_alignment
        if dmarc_percentage is not None:
            self._values["dmarc_percentage"] = dmarc_percentage
        if dmarc_spf_alignment is not None:
            self._values["dmarc_spf_alignment"] = dmarc_spf_alignment
        if dmarc_subdomain_policy is not None:
            self._values["dmarc_subdomain_policy"] = dmarc_subdomain_policy
        if email_address is not None:
            self._values["email_address"] = email_address

    @builtins.property
    def dmarc_policy(self) -> DmarcPolicy:
        '''The DMARC policy to apply to messages that fail DMARC compliance.

        This can be one of the following values:

        - none: Do not apply any special handling to messages that fail DMARC compliance.
        - quarantine: Quarantine messages that fail DMARC compliance.
        - reject: Reject messages that fail DMARC compliance.
        '''
        result = self._values.get("dmarc_policy")
        assert result is not None, "Required property 'dmarc_policy' is missing"
        return typing.cast(DmarcPolicy, result)

    @builtins.property
    def function(self) -> _aws_cdk_aws_lambda_ceddda9d.IFunction:
        '''A Lambda function to invoke after the message is saved to S3.

        The Lambda
        function will be invoked with a SESMessage as event.
        '''
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.IFunction, result)

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The Route 53 hosted zone to create the DMARC record in.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    @builtins.property
    def receipt_rule_set(self) -> _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet:
        '''The SES receipt rule set where a receipt rule will be added.'''
        result = self._values.get("receipt_rule_set")
        assert result is not None, "Required property 'receipt_rule_set' is missing"
        return typing.cast(_aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet, result)

    @builtins.property
    def additional_email_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional email addresses to send DMARC reports to.'''
        result = self._values.get("additional_email_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def after_rule(self) -> typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule]:
        '''An existing rule after which the new rule will be placed in the rule set.

        :default: - The new rule is inserted at the beginning of the rule list.
        '''
        result = self._values.get("after_rule")
        return typing.cast(typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule], result)

    @builtins.property
    def dmarc_dkim_alignment(self) -> typing.Optional[DmarcAlignment]:
        '''The alignment mode to use for DKIM signatures.

        This can be one of the following values:

        - relaxed: Use relaxed alignment mode.
        - strict: Use strict alignment mode.

        :default: relaxed
        '''
        result = self._values.get("dmarc_dkim_alignment")
        return typing.cast(typing.Optional[DmarcAlignment], result)

    @builtins.property
    def dmarc_percentage(self) -> typing.Optional[jsii.Number]:
        '''The percentage of messages that should be checked for DMARC compliance.

        This is a value between 0 and 100.

        :default: 100
        '''
        result = self._values.get("dmarc_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dmarc_spf_alignment(self) -> typing.Optional[DmarcAlignment]:
        '''The alignment mode to use for SPF signatures.

        This can be one of the following values:

        - relaxed: Use relaxed alignment mode.
        - strict: Use strict alignment mode.

        :default: relaxed
        '''
        result = self._values.get("dmarc_spf_alignment")
        return typing.cast(typing.Optional[DmarcAlignment], result)

    @builtins.property
    def dmarc_subdomain_policy(self) -> typing.Optional[DmarcPolicy]:
        '''The DMARC policy to apply to messages that fail DMARC compliance for subdomains.

        This can be one of the following values:

        - none: Do not apply any special handling to messages that fail DMARC compliance.
        - quarantine: Quarantine messages that fail DMARC compliance.
        - reject: Reject messages that fail DMARC compliance.

        :default: inherited from dmarcPolicy
        '''
        result = self._values.get("dmarc_subdomain_policy")
        return typing.cast(typing.Optional[DmarcPolicy], result)

    @builtins.property
    def email_address(self) -> typing.Optional[builtins.str]:
        '''The email address to send DMARC reports to.

        This email address must be verified in SES.

        :default: dmarc-reports@${hostedZone.zoneName}
        '''
        result = self._values.get("email_address")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DmarcReporterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EcsServiceRoller(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.EcsServiceRoller",
):
    '''Roll your ECS service tasks on schedule or with a rule.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        service: _aws_cdk_aws_ecs_ceddda9d.IService,
        trigger: typing.Optional["RollTrigger"] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cluster: The ECS cluster where the services run.
        :param service: The ECS service for which tasks should be rolled.
        :param trigger: The rule or schedule that should trigger a roll. Default: - roll everyday at midnight
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__753ff7415ecea63b65291ecfbbe3c3309a1a616b70c4b0fbba3ebeb929a13136)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EcsServiceRollerProps(
            cluster=cluster, service=service, trigger=trigger
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.EcsServiceRollerProps",
    jsii_struct_bases=[],
    name_mapping={"cluster": "cluster", "service": "service", "trigger": "trigger"},
)
class EcsServiceRollerProps:
    def __init__(
        self,
        *,
        cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
        service: _aws_cdk_aws_ecs_ceddda9d.IService,
        trigger: typing.Optional["RollTrigger"] = None,
    ) -> None:
        '''Properties for a EcsServiceRoller.

        :param cluster: The ECS cluster where the services run.
        :param service: The ECS service for which tasks should be rolled.
        :param trigger: The rule or schedule that should trigger a roll. Default: - roll everyday at midnight
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c382475ffeab1ce7e285837dbf808dbf36902533fcd860db3d3ecfffe47388f)
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument service", value=service, expected_type=type_hints["service"])
            check_type(argname="argument trigger", value=trigger, expected_type=type_hints["trigger"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster": cluster,
            "service": service,
        }
        if trigger is not None:
            self._values["trigger"] = trigger

    @builtins.property
    def cluster(self) -> _aws_cdk_aws_ecs_ceddda9d.ICluster:
        '''The ECS cluster where the services run.'''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.ICluster, result)

    @builtins.property
    def service(self) -> _aws_cdk_aws_ecs_ceddda9d.IService:
        '''The ECS service for which tasks should be rolled.'''
        result = self._values.get("service")
        assert result is not None, "Required property 'service' is missing"
        return typing.cast(_aws_cdk_aws_ecs_ceddda9d.IService, result)

    @builtins.property
    def trigger(self) -> typing.Optional["RollTrigger"]:
        '''The rule or schedule that should trigger a roll.

        :default: - roll everyday at midnight
        '''
        result = self._values.get("trigger")
        return typing.cast(typing.Optional["RollTrigger"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EcsServiceRollerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EmailReceiver(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.EmailReceiver",
):
    '''Receive emails through SES, save them to S3 and invokes a Lambda function.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
        recipients: typing.Sequence[builtins.str],
        after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
        enabled: typing.Optional[builtins.bool] = None,
        function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        source_whitelist: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param receipt_rule_set: The SES receipt rule set where a receipt rule will be added.
        :param recipients: The recipients for which emails should be received.
        :param after_rule: An existing rule after which the new rule will be placed in the rule set. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the receiver is active. Default: true
        :param function: A Lambda function to invoke after the message is saved to S3. The Lambda function will be invoked with a SESMessage as event.
        :param source_whitelist: A regular expression to whitelist source email addresses. Default: - no whitelisting of source email addresses
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2b6712707b39b2d133dd62aef1ea71cf3732c305783f22f76cbafc80508bcaf)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = EmailReceiverProps(
            receipt_rule_set=receipt_rule_set,
            recipients=recipients,
            after_rule=after_rule,
            enabled=enabled,
            function=function,
            source_whitelist=source_whitelist,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''The S3 bucket where emails are delivered.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="topic")
    def topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        '''The SNS topic that is notified when emails are delivered to S3.'''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "topic"))


@jsii.data_type(
    jsii_type="cloudstructs.EmailReceiverProps",
    jsii_struct_bases=[],
    name_mapping={
        "receipt_rule_set": "receiptRuleSet",
        "recipients": "recipients",
        "after_rule": "afterRule",
        "enabled": "enabled",
        "function": "function",
        "source_whitelist": "sourceWhitelist",
    },
)
class EmailReceiverProps:
    def __init__(
        self,
        *,
        receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
        recipients: typing.Sequence[builtins.str],
        after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
        enabled: typing.Optional[builtins.bool] = None,
        function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
        source_whitelist: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for an EmailReceiver.

        :param receipt_rule_set: The SES receipt rule set where a receipt rule will be added.
        :param recipients: The recipients for which emails should be received.
        :param after_rule: An existing rule after which the new rule will be placed in the rule set. Default: - The new rule is inserted at the beginning of the rule list.
        :param enabled: Whether the receiver is active. Default: true
        :param function: A Lambda function to invoke after the message is saved to S3. The Lambda function will be invoked with a SESMessage as event.
        :param source_whitelist: A regular expression to whitelist source email addresses. Default: - no whitelisting of source email addresses
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8500959d1e20d8ab966122bf508b686ba123767348a2c264cc34f3ce69165ae2)
            check_type(argname="argument receipt_rule_set", value=receipt_rule_set, expected_type=type_hints["receipt_rule_set"])
            check_type(argname="argument recipients", value=recipients, expected_type=type_hints["recipients"])
            check_type(argname="argument after_rule", value=after_rule, expected_type=type_hints["after_rule"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument function", value=function, expected_type=type_hints["function"])
            check_type(argname="argument source_whitelist", value=source_whitelist, expected_type=type_hints["source_whitelist"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "receipt_rule_set": receipt_rule_set,
            "recipients": recipients,
        }
        if after_rule is not None:
            self._values["after_rule"] = after_rule
        if enabled is not None:
            self._values["enabled"] = enabled
        if function is not None:
            self._values["function"] = function
        if source_whitelist is not None:
            self._values["source_whitelist"] = source_whitelist

    @builtins.property
    def receipt_rule_set(self) -> _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet:
        '''The SES receipt rule set where a receipt rule will be added.'''
        result = self._values.get("receipt_rule_set")
        assert result is not None, "Required property 'receipt_rule_set' is missing"
        return typing.cast(_aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet, result)

    @builtins.property
    def recipients(self) -> typing.List[builtins.str]:
        '''The recipients for which emails should be received.'''
        result = self._values.get("recipients")
        assert result is not None, "Required property 'recipients' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def after_rule(self) -> typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule]:
        '''An existing rule after which the new rule will be placed in the rule set.

        :default: - The new rule is inserted at the beginning of the rule list.
        '''
        result = self._values.get("after_rule")
        return typing.cast(typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether the receiver is active.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def function(self) -> typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction]:
        '''A Lambda function to invoke after the message is saved to S3.

        The Lambda
        function will be invoked with a SESMessage as event.
        '''
        result = self._values.get("function")
        return typing.cast(typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction], result)

    @builtins.property
    def source_whitelist(self) -> typing.Optional[builtins.str]:
        '''A regular expression to whitelist source email addresses.

        :default: - no whitelisting of source email addresses
        '''
        result = self._values.get("source_whitelist")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EmailReceiverProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="cloudstructs.IStateMachine")
class IStateMachine(typing_extensions.Protocol):
    '''A State Machine.'''

    @builtins.property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine.'''
        ...


class _IStateMachineProxy:
    '''A State Machine.'''

    __jsii_type__: typing.ClassVar[str] = "cloudstructs.IStateMachine"

    @builtins.property
    @jsii.member(jsii_name="stateMachineArn")
    def state_machine_arn(self) -> builtins.str:
        '''The ARN of the state machine.'''
        return typing.cast(builtins.str, jsii.get(self, "stateMachineArn"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IStateMachine).__jsii_proxy_class__ = lambda : _IStateMachineProxy


class MjmlTemplate(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.MjmlTemplate",
):
    '''SES email template from `MJML <https://mjml.io/>`_.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        mjml: builtins.str,
        subject: builtins.str,
        template_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param mjml: The MJML for the email.
        :param subject: The subject line of the email.
        :param template_name: The name of the template. Default: - a CloudFormation generated name
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c14fd1220e2b1a369a0a4b700ec2fd623089a00de406d691f1ebd18fbe576b9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MjmlTemplateProps(
            mjml=mjml, subject=subject, template_name=template_name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="templateName")
    def template_name(self) -> builtins.str:
        '''The name of the template.'''
        return typing.cast(builtins.str, jsii.get(self, "templateName"))


@jsii.data_type(
    jsii_type="cloudstructs.MjmlTemplateProps",
    jsii_struct_bases=[],
    name_mapping={
        "mjml": "mjml",
        "subject": "subject",
        "template_name": "templateName",
    },
)
class MjmlTemplateProps:
    def __init__(
        self,
        *,
        mjml: builtins.str,
        subject: builtins.str,
        template_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for a MjmlTemplate.

        :param mjml: The MJML for the email.
        :param subject: The subject line of the email.
        :param template_name: The name of the template. Default: - a CloudFormation generated name
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__702b570f1be82d9279663f13742ac81b522b758421dbf6217639f90302a51319)
            check_type(argname="argument mjml", value=mjml, expected_type=type_hints["mjml"])
            check_type(argname="argument subject", value=subject, expected_type=type_hints["subject"])
            check_type(argname="argument template_name", value=template_name, expected_type=type_hints["template_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "mjml": mjml,
            "subject": subject,
        }
        if template_name is not None:
            self._values["template_name"] = template_name

    @builtins.property
    def mjml(self) -> builtins.str:
        '''The MJML for the email.'''
        result = self._values.get("mjml")
        assert result is not None, "Required property 'mjml' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def subject(self) -> builtins.str:
        '''The subject line of the email.'''
        result = self._values.get("subject")
        assert result is not None, "Required property 'subject' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def template_name(self) -> typing.Optional[builtins.str]:
        '''The name of the template.

        :default: - a CloudFormation generated name
        '''
        result = self._values.get("template_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MjmlTemplateProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RollTrigger(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cloudstructs.RollTrigger",
):
    '''The rule or schedule that should trigger a roll.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromRule")
    @builtins.classmethod
    def from_rule(cls, rule: _aws_cdk_aws_events_ceddda9d.Rule) -> "RollTrigger":
        '''Rule that should trigger a roll.

        :param rule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04afa5cfc7c8bd76ded88022a29c6aea3d843c1b85acbd7eee9cf5e3d5f838a6)
            check_type(argname="argument rule", value=rule, expected_type=type_hints["rule"])
        return typing.cast("RollTrigger", jsii.sinvoke(cls, "fromRule", [rule]))

    @jsii.member(jsii_name="fromSchedule")
    @builtins.classmethod
    def from_schedule(
        cls,
        schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
    ) -> "RollTrigger":
        '''Schedule that should trigger a roll.

        :param schedule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0deaf527c94f861e7ddb946f9577b690fc63af2396d1fc1e60144369fbc9f1cf)
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        return typing.cast("RollTrigger", jsii.sinvoke(cls, "fromSchedule", [schedule]))

    @builtins.property
    @jsii.member(jsii_name="rule")
    @abc.abstractmethod
    def rule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Rule]:
        '''Roll rule.

        :default: - roll everyday at midnight
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="schedule")
    @abc.abstractmethod
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''Roll schedule.

        :default: - roll everyday at midnight
        '''
        ...


class _RollTriggerProxy(RollTrigger):
    @builtins.property
    @jsii.member(jsii_name="rule")
    def rule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Rule]:
        '''Roll rule.

        :default: - roll everyday at midnight
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Rule], jsii.get(self, "rule"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''Roll schedule.

        :default: - roll everyday at midnight
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], jsii.get(self, "schedule"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, RollTrigger).__jsii_proxy_class__ = lambda : _RollTriggerProxy


class SamlFederatedPrincipal(
    _aws_cdk_aws_iam_ceddda9d.FederatedPrincipal,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SamlFederatedPrincipal",
):
    '''(deprecated) Principal entity that represents a SAML federated identity provider.

    :deprecated: use ``SamlPrincipal`` from ``aws-cdk-lib/aws-iam``

    :stability: deprecated
    '''

    def __init__(self, identity_provider: "SamlIdentityProvider") -> None:
        '''
        :param identity_provider: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52a6b959b946204571517a06c24aa681e69d738ec4d7c40fba77a491cc458c59)
            check_type(argname="argument identity_provider", value=identity_provider, expected_type=type_hints["identity_provider"])
        jsii.create(self.__class__, self, [identity_provider])


class SamlIdentityProvider(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SamlIdentityProvider",
):
    '''(deprecated) Create a SAML identity provider.

    :deprecated: use ``SamlProvider`` from ``aws-cdk-lib/aws-iam``

    :stability: deprecated
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        metadata_document: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param metadata_document: (deprecated) An XML document generated by an identity provider (IdP) that supports SAML 2.0. The document includes the issuer's name, expiration information, and keys that can be used to validate the SAML authentication response (assertions) that are received from the IdP. You must generate the metadata document using the identity management software that is used as your organization's IdP.
        :param name: (deprecated) A name for the SAML identity provider. Default: - derived for the node's unique id

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a951b64d20b1aeea237a4b8d92c7fdf172eac09779a2608ad7de3f809f4eaa13)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SamlIdentityProviderProps(
            metadata_document=metadata_document, name=name
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="samlIdentityProviderArn")
    def saml_identity_provider_arn(self) -> builtins.str:
        '''(deprecated) The ARN of the SAML identity provider.

        :stability: deprecated
        '''
        return typing.cast(builtins.str, jsii.get(self, "samlIdentityProviderArn"))


@jsii.data_type(
    jsii_type="cloudstructs.SamlIdentityProviderProps",
    jsii_struct_bases=[],
    name_mapping={"metadata_document": "metadataDocument", "name": "name"},
)
class SamlIdentityProviderProps:
    def __init__(
        self,
        *,
        metadata_document: builtins.str,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(deprecated) Properties for a SamlProvider.

        :param metadata_document: (deprecated) An XML document generated by an identity provider (IdP) that supports SAML 2.0. The document includes the issuer's name, expiration information, and keys that can be used to validate the SAML authentication response (assertions) that are received from the IdP. You must generate the metadata document using the identity management software that is used as your organization's IdP.
        :param name: (deprecated) A name for the SAML identity provider. Default: - derived for the node's unique id

        :deprecated: use ``SamlProviderProps`` from ``aws-cdk-lib/aws-iam``

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f9fcdf914a540045500dda8934754c0881bc068d0e619a7a76f6379fb77e9d4)
            check_type(argname="argument metadata_document", value=metadata_document, expected_type=type_hints["metadata_document"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metadata_document": metadata_document,
        }
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def metadata_document(self) -> builtins.str:
        '''(deprecated) An XML document generated by an identity provider (IdP) that supports SAML 2.0.

        The document includes the issuer's name, expiration information, and keys that
        can be used to validate the SAML authentication response (assertions) that are
        received from the IdP. You must generate the metadata document using the identity
        management software that is used as your organization's IdP.

        :stability: deprecated
        '''
        result = self._values.get("metadata_document")
        assert result is not None, "Required property 'metadata_document' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(deprecated) A name for the SAML identity provider.

        :default: - derived for the node's unique id

        :stability: deprecated
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SamlIdentityProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackApp(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackApp",
):
    '''A Slack application deployed with a manifest.

    :see: https://api.slack.com/reference/manifests
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        configuration_token_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        manifest: "SlackAppManifestDefinition",
        credentials_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param configuration_token_secret: An AWS Secrets Manager secret containing the app configuration token. Must use the following JSON format:: { "refreshToken": "<token>" }
        :param manifest: The definition of the app manifest.
        :param credentials_secret: The AWS Secrets Manager secret where to store the app credentials. Default: - a new secret is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__465b057c57a03fb90832edc94826ab9fb04f18aca74f9db74978e3764dda2d61)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SlackAppProps(
            configuration_token_secret=configuration_token_secret,
            manifest=manifest,
            credentials_secret=credentials_secret,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        '''The ID of the application.'''
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        '''A dynamic reference to the client ID of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @builtins.property
    @jsii.member(jsii_name="clientSecret")
    def client_secret(self) -> builtins.str:
        '''A dynamic reference to the client secret of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "clientSecret"))

    @builtins.property
    @jsii.member(jsii_name="credentials")
    def credentials(self) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''An AWS Secrets Manager secret containing the credentials of the application.

        Example::

           {
             "appId": "...",
             "clientId": "...",
             "clientSecret": "...",
             "verificationToken": "...",
             "signingSecret": "..."
           }
        '''
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, jsii.get(self, "credentials"))

    @builtins.property
    @jsii.member(jsii_name="signingSecret")
    def signing_secret(self) -> builtins.str:
        '''A dynamic reference to the signing secret of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "signingSecret"))

    @builtins.property
    @jsii.member(jsii_name="verificationToken")
    def verification_token(self) -> builtins.str:
        '''A dynamic reference to the verification token of the app.'''
        return typing.cast(builtins.str, jsii.get(self, "verificationToken"))


class SlackAppManifest(
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackAppManifest",
):
    '''A Slack app manifest.

    :see: https://api.slack.com/reference/manifests
    '''

    def __init__(
        self,
        *,
        name: builtins.str,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_home: typing.Optional[typing.Union["SlackAppManifestAppHome", typing.Dict[builtins.str, typing.Any]]] = None,
        background_color: typing.Optional[builtins.str] = None,
        bot_user: typing.Optional[typing.Union["SlackkAppManifestBotUser", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        event_subscriptions: typing.Optional[typing.Union["SlackAppManifestEventSubscriptions", typing.Dict[builtins.str, typing.Any]]] = None,
        interactivity: typing.Optional[typing.Union["SlackAppManifestInteractivity", typing.Dict[builtins.str, typing.Any]]] = None,
        long_description: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        minor_version: typing.Optional[jsii.Number] = None,
        oauth_config: typing.Optional[typing.Union["SlackAppManifestOauthConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        shortcuts: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestShortcut", typing.Dict[builtins.str, typing.Any]]]] = None,
        slash_commands: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestSlashCommand", typing.Dict[builtins.str, typing.Any]]]] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
        unfurl_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_steps: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestWorkflowStep", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''
        :param name: The name of the app. Maximum length is 35 characters.
        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param app_home: App Home configuration.
        :param background_color: A hex color value that specifies the background color used on hovercards that display information about your app. Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        :param bot_user: Bot user configuration.
        :param description: A short description of the app for display to users. Maximum length is 140 characters. Default: - no short description
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param long_description: A longer version of the description of the app. Maximum length is 4000 characters.
        :param major_version: The major version of the manifest schema to target. Default: - do not target a specific major version
        :param minor_version: The minor version of the manifest schema to target. Default: - do not target a specific minor version
        :param oauth_config: OAuth configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param shortcuts: Shortcuts configuration. A maximum of 5 shortcuts can be included.
        :param slash_commands: Slash commands configuration. A maximum of 5 slash commands can be included.
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        :param unfurl_domains: Valid unfurl domains to register. A maximum of 5 unfurl domains can be included.
        :param workflow_steps: Workflow steps. A maximum of 10 workflow steps can be included.
        '''
        props = SlackAppManifestProps(
            name=name,
            allowed_ip_address_ranges=allowed_ip_address_ranges,
            app_home=app_home,
            background_color=background_color,
            bot_user=bot_user,
            description=description,
            event_subscriptions=event_subscriptions,
            interactivity=interactivity,
            long_description=long_description,
            major_version=major_version,
            minor_version=minor_version,
            oauth_config=oauth_config,
            org_deploy=org_deploy,
            shortcuts=shortcuts,
            slash_commands=slash_commands,
            socket_mode=socket_mode,
            unfurl_domains=unfurl_domains,
            workflow_steps=workflow_steps,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="render")
    def render(self, construct: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''
        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c292ea7dcd606ba7b5b1c30bd9f20d3c9e3a97b2fd901078fbde4ee5d4141f98)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(builtins.str, jsii.invoke(self, "render", [construct]))


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestAppHome",
    jsii_struct_bases=[],
    name_mapping={
        "home_tab": "homeTab",
        "messages_tab": "messagesTab",
        "messages_tab_read_only": "messagesTabReadOnly",
    },
)
class SlackAppManifestAppHome:
    def __init__(
        self,
        *,
        home_tab: typing.Optional[builtins.bool] = None,
        messages_tab: typing.Optional[builtins.bool] = None,
        messages_tab_read_only: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''App Home configuration.

        :param home_tab: Wether the Home tab is enabled. Default: false
        :param messages_tab: Wether the Messages is enabled. Default: false
        :param messages_tab_read_only: Whether the users can send messages to your app in the Messages tab of your App Home. Default: false

        :see: https://api.slack.com/surfaces/tabs
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebc564e9f94fc31e05482aae2aea3411ba92076e3c728589a206f8a9d9da9fc1)
            check_type(argname="argument home_tab", value=home_tab, expected_type=type_hints["home_tab"])
            check_type(argname="argument messages_tab", value=messages_tab, expected_type=type_hints["messages_tab"])
            check_type(argname="argument messages_tab_read_only", value=messages_tab_read_only, expected_type=type_hints["messages_tab_read_only"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if home_tab is not None:
            self._values["home_tab"] = home_tab
        if messages_tab is not None:
            self._values["messages_tab"] = messages_tab
        if messages_tab_read_only is not None:
            self._values["messages_tab_read_only"] = messages_tab_read_only

    @builtins.property
    def home_tab(self) -> typing.Optional[builtins.bool]:
        '''Wether the Home tab is enabled.

        :default: false
        '''
        result = self._values.get("home_tab")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def messages_tab(self) -> typing.Optional[builtins.bool]:
        '''Wether the Messages is enabled.

        :default: false
        '''
        result = self._values.get("messages_tab")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def messages_tab_read_only(self) -> typing.Optional[builtins.bool]:
        '''Whether the users can send messages to your app in the Messages tab of your App Home.

        :default: false
        '''
        result = self._values.get("messages_tab_read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestAppHome(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackAppManifestDefinition(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cloudstructs.SlackAppManifestDefinition",
):
    '''A Slack app manifest definition.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromFile")
    @builtins.classmethod
    def from_file(cls, file: builtins.str) -> "SlackAppManifestDefinition":
        '''Creates a Slack app manifest from a file containg a JSON app manifest.

        :param file: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9861cffdd6158b4e677b4da06928ef6a7b9bd623beacbc39060fc371dae6df2d)
            check_type(argname="argument file", value=file, expected_type=type_hints["file"])
        return typing.cast("SlackAppManifestDefinition", jsii.sinvoke(cls, "fromFile", [file]))

    @jsii.member(jsii_name="fromManifest")
    @builtins.classmethod
    def from_manifest(
        cls,
        *,
        name: builtins.str,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_home: typing.Optional[typing.Union[SlackAppManifestAppHome, typing.Dict[builtins.str, typing.Any]]] = None,
        background_color: typing.Optional[builtins.str] = None,
        bot_user: typing.Optional[typing.Union["SlackkAppManifestBotUser", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        event_subscriptions: typing.Optional[typing.Union["SlackAppManifestEventSubscriptions", typing.Dict[builtins.str, typing.Any]]] = None,
        interactivity: typing.Optional[typing.Union["SlackAppManifestInteractivity", typing.Dict[builtins.str, typing.Any]]] = None,
        long_description: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        minor_version: typing.Optional[jsii.Number] = None,
        oauth_config: typing.Optional[typing.Union["SlackAppManifestOauthConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        shortcuts: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestShortcut", typing.Dict[builtins.str, typing.Any]]]] = None,
        slash_commands: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestSlashCommand", typing.Dict[builtins.str, typing.Any]]]] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
        unfurl_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_steps: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestWorkflowStep", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> "SlackAppManifestDefinition":
        '''Creates a Slack app manifest by specifying properties.

        :param name: The name of the app. Maximum length is 35 characters.
        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param app_home: App Home configuration.
        :param background_color: A hex color value that specifies the background color used on hovercards that display information about your app. Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        :param bot_user: Bot user configuration.
        :param description: A short description of the app for display to users. Maximum length is 140 characters. Default: - no short description
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param long_description: A longer version of the description of the app. Maximum length is 4000 characters.
        :param major_version: The major version of the manifest schema to target. Default: - do not target a specific major version
        :param minor_version: The minor version of the manifest schema to target. Default: - do not target a specific minor version
        :param oauth_config: OAuth configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param shortcuts: Shortcuts configuration. A maximum of 5 shortcuts can be included.
        :param slash_commands: Slash commands configuration. A maximum of 5 slash commands can be included.
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        :param unfurl_domains: Valid unfurl domains to register. A maximum of 5 unfurl domains can be included.
        :param workflow_steps: Workflow steps. A maximum of 10 workflow steps can be included.
        '''
        props = SlackAppManifestProps(
            name=name,
            allowed_ip_address_ranges=allowed_ip_address_ranges,
            app_home=app_home,
            background_color=background_color,
            bot_user=bot_user,
            description=description,
            event_subscriptions=event_subscriptions,
            interactivity=interactivity,
            long_description=long_description,
            major_version=major_version,
            minor_version=minor_version,
            oauth_config=oauth_config,
            org_deploy=org_deploy,
            shortcuts=shortcuts,
            slash_commands=slash_commands,
            socket_mode=socket_mode,
            unfurl_domains=unfurl_domains,
            workflow_steps=workflow_steps,
        )

        return typing.cast("SlackAppManifestDefinition", jsii.sinvoke(cls, "fromManifest", [props]))

    @jsii.member(jsii_name="fromString")
    @builtins.classmethod
    def from_string(cls, manifest: builtins.str) -> "SlackAppManifestDefinition":
        '''Create a Slack app manifest from a JSON app manifest encoded as a string.

        :param manifest: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__442948d30bfd13d2eb21cb8bfe977e866d481c4426e25e028a24219a78a44451)
            check_type(argname="argument manifest", value=manifest, expected_type=type_hints["manifest"])
        return typing.cast("SlackAppManifestDefinition", jsii.sinvoke(cls, "fromString", [manifest]))

    @jsii.member(jsii_name="render")
    @abc.abstractmethod
    def render(self, construct: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''Renders the JSON app manifest encoded as a string.

        :param construct: -
        '''
        ...


class _SlackAppManifestDefinitionProxy(SlackAppManifestDefinition):
    @jsii.member(jsii_name="render")
    def render(self, construct: _constructs_77d1e7e8.IConstruct) -> builtins.str:
        '''Renders the JSON app manifest encoded as a string.

        :param construct: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33c88afd12de1290db0923503493054b4d8e13085afa9cbb8c4185f83aaa951c)
            check_type(argname="argument construct", value=construct, expected_type=type_hints["construct"])
        return typing.cast(builtins.str, jsii.invoke(self, "render", [construct]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, SlackAppManifestDefinition).__jsii_proxy_class__ = lambda : _SlackAppManifestDefinitionProxy


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestEventSubscriptions",
    jsii_struct_bases=[],
    name_mapping={
        "request_url": "requestUrl",
        "bot_events": "botEvents",
        "user_events": "userEvents",
    },
)
class SlackAppManifestEventSubscriptions:
    def __init__(
        self,
        *,
        request_url: builtins.str,
        bot_events: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_events: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Events API configuration for the app.

        :param request_url: The full https URL that acts as the Events API request URL.
        :param bot_events: Event types you want the app to subscribe to. A maximum of 100 event types can be used
        :param user_events: Event types you want the app to subscribe to on behalf of authorized users. A maximum of 100 event types can be used.

        :see: https://api.slack.com/events-api
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f760e51128fe54d75e4283960678989fab49ecddde79deec8d2aab9b20e430d7)
            check_type(argname="argument request_url", value=request_url, expected_type=type_hints["request_url"])
            check_type(argname="argument bot_events", value=bot_events, expected_type=type_hints["bot_events"])
            check_type(argname="argument user_events", value=user_events, expected_type=type_hints["user_events"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "request_url": request_url,
        }
        if bot_events is not None:
            self._values["bot_events"] = bot_events
        if user_events is not None:
            self._values["user_events"] = user_events

    @builtins.property
    def request_url(self) -> builtins.str:
        '''The full https URL that acts as the Events API request URL.

        :see: https://api.slack.com/events-api#the-events-api__subscribing-to-event-types__events-api-request-urls
        '''
        result = self._values.get("request_url")
        assert result is not None, "Required property 'request_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bot_events(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Event types you want the app to subscribe to.

        A maximum of 100 event types can be used

        :see: https://api.slack.com/events
        '''
        result = self._values.get("bot_events")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_events(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Event types you want the app to subscribe to on behalf of authorized users.

        A maximum of 100 event types can be used.
        '''
        result = self._values.get("user_events")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestEventSubscriptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestInteractivity",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "message_menu_options_url": "messageMenuOptionsUrl",
        "request_url": "requestUrl",
    },
)
class SlackAppManifestInteractivity:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        message_menu_options_url: typing.Optional[builtins.str] = None,
        request_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Interactivity configuration for the app.

        :param enabled: Whether or not interactivity features are enabled. Default: true
        :param message_menu_options_url: The full https URL that acts as th interactive Options Load URL.
        :param request_url: The full https URL that acts as the interactive Request URL.

        :see: https://api.slack.com/interactivity/handling#setup
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e58235c45e7590fe9814bb419867acbcd4af8fc1b7f672d36385a0c7a6a1df3b)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument message_menu_options_url", value=message_menu_options_url, expected_type=type_hints["message_menu_options_url"])
            check_type(argname="argument request_url", value=request_url, expected_type=type_hints["request_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if message_menu_options_url is not None:
            self._values["message_menu_options_url"] = message_menu_options_url
        if request_url is not None:
            self._values["request_url"] = request_url

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether or not interactivity features are enabled.

        :default: true
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def message_menu_options_url(self) -> typing.Optional[builtins.str]:
        '''The full https URL that acts as th interactive Options Load URL.'''
        result = self._values.get("message_menu_options_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_url(self) -> typing.Optional[builtins.str]:
        '''The full https URL that acts as the interactive Request URL.'''
        result = self._values.get("request_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestInteractivity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestOauthConfig",
    jsii_struct_bases=[],
    name_mapping={
        "bot_scopes": "botScopes",
        "redirect_urls": "redirectUrls",
        "user_scopes": "userScopes",
    },
)
class SlackAppManifestOauthConfig:
    def __init__(
        self,
        *,
        bot_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        redirect_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''OAuth configuration for the app.

        :param bot_scopes: Bot scopes to request upon app installation. A maximum of 255 scopes can be included.
        :param redirect_urls: OAuth redirect URLs. A maximum of 1000 redirect URLs can be included.
        :param user_scopes: User scopes to request upon app installation. A maximum of 255 scopes can be included.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a4285b701f803583267e7d3fabf4f0d5927a0963c2907bb137ad64fd34321c5)
            check_type(argname="argument bot_scopes", value=bot_scopes, expected_type=type_hints["bot_scopes"])
            check_type(argname="argument redirect_urls", value=redirect_urls, expected_type=type_hints["redirect_urls"])
            check_type(argname="argument user_scopes", value=user_scopes, expected_type=type_hints["user_scopes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bot_scopes is not None:
            self._values["bot_scopes"] = bot_scopes
        if redirect_urls is not None:
            self._values["redirect_urls"] = redirect_urls
        if user_scopes is not None:
            self._values["user_scopes"] = user_scopes

    @builtins.property
    def bot_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Bot scopes to request upon app installation.

        A maximum of 255 scopes can be included.

        :see: https://api.slack.com/scopes
        '''
        result = self._values.get("bot_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def redirect_urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''OAuth redirect URLs.

        A maximum of 1000 redirect URLs can be included.

        :see: https://api.slack.com/authentication/oauth-v2#redirect_urls
        '''
        result = self._values.get("redirect_urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''User scopes to request upon app installation.

        A maximum of 255 scopes can be included.

        :see: https://api.slack.com/scopes
        '''
        result = self._values.get("user_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestOauthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestProps",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "allowed_ip_address_ranges": "allowedIpAddressRanges",
        "app_home": "appHome",
        "background_color": "backgroundColor",
        "bot_user": "botUser",
        "description": "description",
        "event_subscriptions": "eventSubscriptions",
        "interactivity": "interactivity",
        "long_description": "longDescription",
        "major_version": "majorVersion",
        "minor_version": "minorVersion",
        "oauth_config": "oauthConfig",
        "org_deploy": "orgDeploy",
        "shortcuts": "shortcuts",
        "slash_commands": "slashCommands",
        "socket_mode": "socketMode",
        "unfurl_domains": "unfurlDomains",
        "workflow_steps": "workflowSteps",
    },
)
class SlackAppManifestProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        app_home: typing.Optional[typing.Union[SlackAppManifestAppHome, typing.Dict[builtins.str, typing.Any]]] = None,
        background_color: typing.Optional[builtins.str] = None,
        bot_user: typing.Optional[typing.Union["SlackkAppManifestBotUser", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        event_subscriptions: typing.Optional[typing.Union[SlackAppManifestEventSubscriptions, typing.Dict[builtins.str, typing.Any]]] = None,
        interactivity: typing.Optional[typing.Union[SlackAppManifestInteractivity, typing.Dict[builtins.str, typing.Any]]] = None,
        long_description: typing.Optional[builtins.str] = None,
        major_version: typing.Optional[jsii.Number] = None,
        minor_version: typing.Optional[jsii.Number] = None,
        oauth_config: typing.Optional[typing.Union[SlackAppManifestOauthConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        shortcuts: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestShortcut", typing.Dict[builtins.str, typing.Any]]]] = None,
        slash_commands: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestSlashCommand", typing.Dict[builtins.str, typing.Any]]]] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
        unfurl_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        workflow_steps: typing.Optional[typing.Sequence[typing.Union["SlackAppManifestWorkflowStep", typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> None:
        '''Properties for a Slack app manifest.

        :param name: The name of the app. Maximum length is 35 characters.
        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param app_home: App Home configuration.
        :param background_color: A hex color value that specifies the background color used on hovercards that display information about your app. Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        :param bot_user: Bot user configuration.
        :param description: A short description of the app for display to users. Maximum length is 140 characters. Default: - no short description
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param long_description: A longer version of the description of the app. Maximum length is 4000 characters.
        :param major_version: The major version of the manifest schema to target. Default: - do not target a specific major version
        :param minor_version: The minor version of the manifest schema to target. Default: - do not target a specific minor version
        :param oauth_config: OAuth configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param shortcuts: Shortcuts configuration. A maximum of 5 shortcuts can be included.
        :param slash_commands: Slash commands configuration. A maximum of 5 slash commands can be included.
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        :param unfurl_domains: Valid unfurl domains to register. A maximum of 5 unfurl domains can be included.
        :param workflow_steps: Workflow steps. A maximum of 10 workflow steps can be included.

        :see: https://api.slack.com/reference/manifests
        '''
        if isinstance(app_home, dict):
            app_home = SlackAppManifestAppHome(**app_home)
        if isinstance(bot_user, dict):
            bot_user = SlackkAppManifestBotUser(**bot_user)
        if isinstance(event_subscriptions, dict):
            event_subscriptions = SlackAppManifestEventSubscriptions(**event_subscriptions)
        if isinstance(interactivity, dict):
            interactivity = SlackAppManifestInteractivity(**interactivity)
        if isinstance(oauth_config, dict):
            oauth_config = SlackAppManifestOauthConfig(**oauth_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74c65eb0c2898e68978843e3401e2c4a6e49e561b964c1b7179ecbe9546b2022)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument allowed_ip_address_ranges", value=allowed_ip_address_ranges, expected_type=type_hints["allowed_ip_address_ranges"])
            check_type(argname="argument app_home", value=app_home, expected_type=type_hints["app_home"])
            check_type(argname="argument background_color", value=background_color, expected_type=type_hints["background_color"])
            check_type(argname="argument bot_user", value=bot_user, expected_type=type_hints["bot_user"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument event_subscriptions", value=event_subscriptions, expected_type=type_hints["event_subscriptions"])
            check_type(argname="argument interactivity", value=interactivity, expected_type=type_hints["interactivity"])
            check_type(argname="argument long_description", value=long_description, expected_type=type_hints["long_description"])
            check_type(argname="argument major_version", value=major_version, expected_type=type_hints["major_version"])
            check_type(argname="argument minor_version", value=minor_version, expected_type=type_hints["minor_version"])
            check_type(argname="argument oauth_config", value=oauth_config, expected_type=type_hints["oauth_config"])
            check_type(argname="argument org_deploy", value=org_deploy, expected_type=type_hints["org_deploy"])
            check_type(argname="argument shortcuts", value=shortcuts, expected_type=type_hints["shortcuts"])
            check_type(argname="argument slash_commands", value=slash_commands, expected_type=type_hints["slash_commands"])
            check_type(argname="argument socket_mode", value=socket_mode, expected_type=type_hints["socket_mode"])
            check_type(argname="argument unfurl_domains", value=unfurl_domains, expected_type=type_hints["unfurl_domains"])
            check_type(argname="argument workflow_steps", value=workflow_steps, expected_type=type_hints["workflow_steps"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if allowed_ip_address_ranges is not None:
            self._values["allowed_ip_address_ranges"] = allowed_ip_address_ranges
        if app_home is not None:
            self._values["app_home"] = app_home
        if background_color is not None:
            self._values["background_color"] = background_color
        if bot_user is not None:
            self._values["bot_user"] = bot_user
        if description is not None:
            self._values["description"] = description
        if event_subscriptions is not None:
            self._values["event_subscriptions"] = event_subscriptions
        if interactivity is not None:
            self._values["interactivity"] = interactivity
        if long_description is not None:
            self._values["long_description"] = long_description
        if major_version is not None:
            self._values["major_version"] = major_version
        if minor_version is not None:
            self._values["minor_version"] = minor_version
        if oauth_config is not None:
            self._values["oauth_config"] = oauth_config
        if org_deploy is not None:
            self._values["org_deploy"] = org_deploy
        if shortcuts is not None:
            self._values["shortcuts"] = shortcuts
        if slash_commands is not None:
            self._values["slash_commands"] = slash_commands
        if socket_mode is not None:
            self._values["socket_mode"] = socket_mode
        if unfurl_domains is not None:
            self._values["unfurl_domains"] = unfurl_domains
        if workflow_steps is not None:
            self._values["workflow_steps"] = workflow_steps

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the app.

        Maximum length is 35 characters.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def allowed_ip_address_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of IP addresses that conform to the Allowed IP Ranges feature.

        :see: https://api.slack.com/authentication/best-practices#ip_allowlisting
        '''
        result = self._values.get("allowed_ip_address_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def app_home(self) -> typing.Optional[SlackAppManifestAppHome]:
        '''App Home configuration.

        :see: https://api.slack.com/surfaces/tabs
        '''
        result = self._values.get("app_home")
        return typing.cast(typing.Optional[SlackAppManifestAppHome], result)

    @builtins.property
    def background_color(self) -> typing.Optional[builtins.str]:
        '''A hex color value that specifies the background color used on hovercards that display information about your app.

        Can be 3-digit (#000) or 6-digit (#000000) hex values with or without #
        '''
        result = self._values.get("background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bot_user(self) -> typing.Optional["SlackkAppManifestBotUser"]:
        '''Bot user configuration.

        :see: https://api.slack.com/bot-users
        '''
        result = self._values.get("bot_user")
        return typing.cast(typing.Optional["SlackkAppManifestBotUser"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''A short description of the app for display to users.

        Maximum length is 140 characters.

        :default: - no short description
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def event_subscriptions(
        self,
    ) -> typing.Optional[SlackAppManifestEventSubscriptions]:
        '''Events API configuration for the app.

        :see: https://api.slack.com/events-api
        '''
        result = self._values.get("event_subscriptions")
        return typing.cast(typing.Optional[SlackAppManifestEventSubscriptions], result)

    @builtins.property
    def interactivity(self) -> typing.Optional[SlackAppManifestInteractivity]:
        '''Interactivity configuration for the app.'''
        result = self._values.get("interactivity")
        return typing.cast(typing.Optional[SlackAppManifestInteractivity], result)

    @builtins.property
    def long_description(self) -> typing.Optional[builtins.str]:
        '''A longer version of the description of the app.

        Maximum length is 4000 characters.
        '''
        result = self._values.get("long_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def major_version(self) -> typing.Optional[jsii.Number]:
        '''The major version of the manifest schema to target.

        :default: - do not target a specific major version
        '''
        result = self._values.get("major_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minor_version(self) -> typing.Optional[jsii.Number]:
        '''The minor version of the manifest schema to target.

        :default: - do not target a specific minor version
        '''
        result = self._values.get("minor_version")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def oauth_config(self) -> typing.Optional[SlackAppManifestOauthConfig]:
        '''OAuth configuration for the app.'''
        result = self._values.get("oauth_config")
        return typing.cast(typing.Optional[SlackAppManifestOauthConfig], result)

    @builtins.property
    def org_deploy(self) -> typing.Optional[builtins.bool]:
        '''Whether org-wide deploy is enabled.

        :default: false

        :see: https://api.slack.com/enterprise/apps
        '''
        result = self._values.get("org_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def shortcuts(self) -> typing.Optional[typing.List["SlackAppManifestShortcut"]]:
        '''Shortcuts configuration.

        A maximum of 5 shortcuts can be included.

        :see: https://api.slack.com/interactivity/shortcuts
        '''
        result = self._values.get("shortcuts")
        return typing.cast(typing.Optional[typing.List["SlackAppManifestShortcut"]], result)

    @builtins.property
    def slash_commands(
        self,
    ) -> typing.Optional[typing.List["SlackAppManifestSlashCommand"]]:
        '''Slash commands configuration.

        A maximum of 5 slash commands can be included.

        :see: https://api.slack.com/interactivity/slash-commands
        '''
        result = self._values.get("slash_commands")
        return typing.cast(typing.Optional[typing.List["SlackAppManifestSlashCommand"]], result)

    @builtins.property
    def socket_mode(self) -> typing.Optional[builtins.bool]:
        '''Whether Socket Mode is enabled.

        :default: false

        :see: https://api.slack.com/apis/connections/socket
        '''
        result = self._values.get("socket_mode")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def unfurl_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Valid unfurl domains to register.

        A maximum of 5 unfurl domains can be included.

        :see: https://api.slack.com/reference/messaging/link-unfurling#configuring_domains
        '''
        result = self._values.get("unfurl_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def workflow_steps(
        self,
    ) -> typing.Optional[typing.List["SlackAppManifestWorkflowStep"]]:
        '''Workflow steps.

        A maximum of 10 workflow steps can be included.

        :see: https://api.slack.com/workflows/steps
        '''
        result = self._values.get("workflow_steps")
        return typing.cast(typing.Optional[typing.List["SlackAppManifestWorkflowStep"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestSettings",
    jsii_struct_bases=[],
    name_mapping={
        "allowed_ip_address_ranges": "allowedIpAddressRanges",
        "event_subscriptions": "eventSubscriptions",
        "interactivity": "interactivity",
        "org_deploy": "orgDeploy",
        "socket_mode": "socketMode",
    },
)
class SlackAppManifestSettings:
    def __init__(
        self,
        *,
        allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
        event_subscriptions: typing.Optional[typing.Union[SlackAppManifestEventSubscriptions, typing.Dict[builtins.str, typing.Any]]] = None,
        interactivity: typing.Optional[typing.Union[SlackAppManifestInteractivity, typing.Dict[builtins.str, typing.Any]]] = None,
        org_deploy: typing.Optional[builtins.bool] = None,
        socket_mode: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Settings section of the app config pages.

        :param allowed_ip_address_ranges: An array of IP addresses that conform to the Allowed IP Ranges feature.
        :param event_subscriptions: Events API configuration for the app.
        :param interactivity: Interactivity configuration for the app.
        :param org_deploy: Whether org-wide deploy is enabled. Default: false
        :param socket_mode: Whether Socket Mode is enabled. Default: false
        '''
        if isinstance(event_subscriptions, dict):
            event_subscriptions = SlackAppManifestEventSubscriptions(**event_subscriptions)
        if isinstance(interactivity, dict):
            interactivity = SlackAppManifestInteractivity(**interactivity)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae6cef8f97993e8837c36e28365e7d270ee7de63f7ad8a03151bf8157d3c9a9b)
            check_type(argname="argument allowed_ip_address_ranges", value=allowed_ip_address_ranges, expected_type=type_hints["allowed_ip_address_ranges"])
            check_type(argname="argument event_subscriptions", value=event_subscriptions, expected_type=type_hints["event_subscriptions"])
            check_type(argname="argument interactivity", value=interactivity, expected_type=type_hints["interactivity"])
            check_type(argname="argument org_deploy", value=org_deploy, expected_type=type_hints["org_deploy"])
            check_type(argname="argument socket_mode", value=socket_mode, expected_type=type_hints["socket_mode"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allowed_ip_address_ranges is not None:
            self._values["allowed_ip_address_ranges"] = allowed_ip_address_ranges
        if event_subscriptions is not None:
            self._values["event_subscriptions"] = event_subscriptions
        if interactivity is not None:
            self._values["interactivity"] = interactivity
        if org_deploy is not None:
            self._values["org_deploy"] = org_deploy
        if socket_mode is not None:
            self._values["socket_mode"] = socket_mode

    @builtins.property
    def allowed_ip_address_ranges(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of IP addresses that conform to the Allowed IP Ranges feature.

        :see: https://api.slack.com/authentication/best-practices#ip_allowlisting
        '''
        result = self._values.get("allowed_ip_address_ranges")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def event_subscriptions(
        self,
    ) -> typing.Optional[SlackAppManifestEventSubscriptions]:
        '''Events API configuration for the app.

        :see: https://api.slack.com/events-api
        '''
        result = self._values.get("event_subscriptions")
        return typing.cast(typing.Optional[SlackAppManifestEventSubscriptions], result)

    @builtins.property
    def interactivity(self) -> typing.Optional[SlackAppManifestInteractivity]:
        '''Interactivity configuration for the app.'''
        result = self._values.get("interactivity")
        return typing.cast(typing.Optional[SlackAppManifestInteractivity], result)

    @builtins.property
    def org_deploy(self) -> typing.Optional[builtins.bool]:
        '''Whether org-wide deploy is enabled.

        :default: false

        :see: https://api.slack.com/enterprise/apps
        '''
        result = self._values.get("org_deploy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def socket_mode(self) -> typing.Optional[builtins.bool]:
        '''Whether Socket Mode is enabled.

        :default: false

        :see: https://api.slack.com/apis/connections/socket
        '''
        result = self._values.get("socket_mode")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestShortcut",
    jsii_struct_bases=[],
    name_mapping={
        "callback_id": "callbackId",
        "description": "description",
        "name": "name",
        "type": "type",
    },
)
class SlackAppManifestShortcut:
    def __init__(
        self,
        *,
        callback_id: builtins.str,
        description: builtins.str,
        name: builtins.str,
        type: "SlackAppManifestShortcutType",
    ) -> None:
        '''Shortcut configuration.

        :param callback_id: The callback ID of the shortcut. Maximum length is 255 characters.
        :param description: A short description of the shortcut. Maximum length is 150 characters
        :param name: The name of the shortcut.
        :param type: The type of shortcut.

        :see: https://api.slack.com/interactivity/shortcuts
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b511717247813827d96471269da9620f5038467fcb8c7f43381dac0722dd0030)
            check_type(argname="argument callback_id", value=callback_id, expected_type=type_hints["callback_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "callback_id": callback_id,
            "description": description,
            "name": name,
            "type": type,
        }

    @builtins.property
    def callback_id(self) -> builtins.str:
        '''The callback ID of the shortcut.

        Maximum length is 255 characters.
        '''
        result = self._values.get("callback_id")
        assert result is not None, "Required property 'callback_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''A short description of the shortcut.

        Maximum length is 150 characters
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the shortcut.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> "SlackAppManifestShortcutType":
        '''The type of shortcut.

        :see: https://api.slack.com/interactivity/shortcuts
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("SlackAppManifestShortcutType", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestShortcut(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cloudstructs.SlackAppManifestShortcutType")
class SlackAppManifestShortcutType(enum.Enum):
    '''Type of shortcuts.

    :see: https://api.slack.com/interactivity/shortcuts
    '''

    MESSAGE = "MESSAGE"
    '''Message shortcuts are shown to users in the context menus of messages within Slack.

    :see: https://api.slack.com/interactivity/shortcuts/using#message_shortcuts
    '''
    GLOBAL = "GLOBAL"
    '''Global shortcuts are available to users via the shortcuts button in the composer, and when using search in Slack.

    :see: https://api.slack.com/interactivity/shortcuts/using#global_shortcuts
    '''


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestSlashCommand",
    jsii_struct_bases=[],
    name_mapping={
        "command": "command",
        "description": "description",
        "should_escape": "shouldEscape",
        "url": "url",
        "usage_hint": "usageHint",
    },
)
class SlackAppManifestSlashCommand:
    def __init__(
        self,
        *,
        command: builtins.str,
        description: builtins.str,
        should_escape: typing.Optional[builtins.bool] = None,
        url: typing.Optional[builtins.str] = None,
        usage_hint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Slash command configuration.

        :param command: The actual slash command. Maximum length is 32 characters
        :param description: The description of the slash command. Maximum length is 2000 characters.
        :param should_escape: Whether channels, users, and links typed with the slash command should be escaped. Default: false
        :param url: The full https URL that acts as the slash command's request URL.
        :param usage_hint: The short usage hint about the slash command for users. Maximum length is 1000 characters.

        :see: https://api.slack.com/interactivity/slash-commands
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3b48421ebf37a276ebe1a2f9723f99362dbf35cdb7f2acb57844b6dc6f1611f)
            check_type(argname="argument command", value=command, expected_type=type_hints["command"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument should_escape", value=should_escape, expected_type=type_hints["should_escape"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument usage_hint", value=usage_hint, expected_type=type_hints["usage_hint"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "command": command,
            "description": description,
        }
        if should_escape is not None:
            self._values["should_escape"] = should_escape
        if url is not None:
            self._values["url"] = url
        if usage_hint is not None:
            self._values["usage_hint"] = usage_hint

    @builtins.property
    def command(self) -> builtins.str:
        '''The actual slash command.

        Maximum length is 32 characters
        '''
        result = self._values.get("command")
        assert result is not None, "Required property 'command' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> builtins.str:
        '''The description of the slash command.

        Maximum length is 2000 characters.
        '''
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def should_escape(self) -> typing.Optional[builtins.bool]:
        '''Whether channels, users, and links typed with the slash command should be escaped.

        :default: false
        '''
        result = self._values.get("should_escape")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''The full https URL that acts as the slash command's request URL.

        :see: https://api.slack.com/interactivity/slash-commands#creating_commands
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usage_hint(self) -> typing.Optional[builtins.str]:
        '''The short usage hint about the slash command for users.

        Maximum length is 1000 characters.
        '''
        result = self._values.get("usage_hint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestSlashCommand(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppManifestWorkflowStep",
    jsii_struct_bases=[],
    name_mapping={"callback_id": "callbackId", "name": "name"},
)
class SlackAppManifestWorkflowStep:
    def __init__(self, *, callback_id: builtins.str, name: builtins.str) -> None:
        '''Workflow step.

        :param callback_id: The callback ID of the workflow step. Maximum length of 50 characters.
        :param name: The name of the workflow step. Maximum length of 50 characters.

        :see: https://api.slack.com/workflows/steps
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72e624e96c2a7571173b90657cfb84ff239679796527e8155c83f02352f63849)
            check_type(argname="argument callback_id", value=callback_id, expected_type=type_hints["callback_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "callback_id": callback_id,
            "name": name,
        }

    @builtins.property
    def callback_id(self) -> builtins.str:
        '''The callback ID of the workflow step.

        Maximum length of 50 characters.
        '''
        result = self._values.get("callback_id")
        assert result is not None, "Required property 'callback_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the workflow step.

        Maximum length of 50 characters.
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppManifestWorkflowStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackAppProps",
    jsii_struct_bases=[],
    name_mapping={
        "configuration_token_secret": "configurationTokenSecret",
        "manifest": "manifest",
        "credentials_secret": "credentialsSecret",
    },
)
class SlackAppProps:
    def __init__(
        self,
        *,
        configuration_token_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
        manifest: SlackAppManifestDefinition,
        credentials_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
    ) -> None:
        '''Properties for a SlackApp.

        :param configuration_token_secret: An AWS Secrets Manager secret containing the app configuration token. Must use the following JSON format:: { "refreshToken": "<token>" }
        :param manifest: The definition of the app manifest.
        :param credentials_secret: The AWS Secrets Manager secret where to store the app credentials. Default: - a new secret is created
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8dd6d3b3477e298be57433e7c12f534278e17d0927c136b7cb0d32ecfc05a8d)
            check_type(argname="argument configuration_token_secret", value=configuration_token_secret, expected_type=type_hints["configuration_token_secret"])
            check_type(argname="argument manifest", value=manifest, expected_type=type_hints["manifest"])
            check_type(argname="argument credentials_secret", value=credentials_secret, expected_type=type_hints["credentials_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "configuration_token_secret": configuration_token_secret,
            "manifest": manifest,
        }
        if credentials_secret is not None:
            self._values["credentials_secret"] = credentials_secret

    @builtins.property
    def configuration_token_secret(
        self,
    ) -> _aws_cdk_aws_secretsmanager_ceddda9d.ISecret:
        '''An AWS Secrets Manager secret containing the app configuration token.

        Must use the following JSON format::

           {
             "refreshToken": "<token>"
           }
        '''
        result = self._values.get("configuration_token_secret")
        assert result is not None, "Required property 'configuration_token_secret' is missing"
        return typing.cast(_aws_cdk_aws_secretsmanager_ceddda9d.ISecret, result)

    @builtins.property
    def manifest(self) -> SlackAppManifestDefinition:
        '''The definition of the app manifest.

        :see: https://api.slack.com/reference/manifests
        '''
        result = self._values.get("manifest")
        assert result is not None, "Required property 'manifest' is missing"
        return typing.cast(SlackAppManifestDefinition, result)

    @builtins.property
    def credentials_secret(
        self,
    ) -> typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret]:
        '''The AWS Secrets Manager secret where to store the app credentials.

        :default: - a new secret is created
        '''
        result = self._values.get("credentials_secret")
        return typing.cast(typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackAppProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackEvents(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackEvents",
):
    '''Send Slack events to Amazon EventBridge.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        signing_secret: _aws_cdk_ceddda9d.SecretValue,
        api_name: typing.Optional[builtins.str] = None,
        custom_event_bus: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param signing_secret: The signing secret of the Slack app.
        :param api_name: A name for the API Gateway resource. Default: SlackEventsApi
        :param custom_event_bus: Whether to use a custom event bus. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__712a11486ef4ddd0a37ce4f4c6116743132220a3f83a522d69417bf554327c80)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SlackEventsProps(
            signing_secret=signing_secret,
            api_name=api_name,
            custom_event_bus=custom_event_bus,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="eventBus")
    def event_bus(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBus]:
        '''The custom event bus where Slack events are sent.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.EventBus], jsii.get(self, "eventBus"))


@jsii.data_type(
    jsii_type="cloudstructs.SlackEventsProps",
    jsii_struct_bases=[],
    name_mapping={
        "signing_secret": "signingSecret",
        "api_name": "apiName",
        "custom_event_bus": "customEventBus",
    },
)
class SlackEventsProps:
    def __init__(
        self,
        *,
        signing_secret: _aws_cdk_ceddda9d.SecretValue,
        api_name: typing.Optional[builtins.str] = None,
        custom_event_bus: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for a SlackEvents.

        :param signing_secret: The signing secret of the Slack app.
        :param api_name: A name for the API Gateway resource. Default: SlackEventsApi
        :param custom_event_bus: Whether to use a custom event bus. Default: false
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__844db98a7fefe45c6d2e05f3b5c81e4e0a5cb3f865f4c32b4622a66121d2bb89)
            check_type(argname="argument signing_secret", value=signing_secret, expected_type=type_hints["signing_secret"])
            check_type(argname="argument api_name", value=api_name, expected_type=type_hints["api_name"])
            check_type(argname="argument custom_event_bus", value=custom_event_bus, expected_type=type_hints["custom_event_bus"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "signing_secret": signing_secret,
        }
        if api_name is not None:
            self._values["api_name"] = api_name
        if custom_event_bus is not None:
            self._values["custom_event_bus"] = custom_event_bus

    @builtins.property
    def signing_secret(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''The signing secret of the Slack app.'''
        result = self._values.get("signing_secret")
        assert result is not None, "Required property 'signing_secret' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def api_name(self) -> typing.Optional[builtins.str]:
        '''A name for the API Gateway resource.

        :default: SlackEventsApi
        '''
        result = self._values.get("api_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def custom_event_bus(self) -> typing.Optional[builtins.bool]:
        '''Whether to use a custom event bus.

        :default: false
        '''
        result = self._values.get("custom_event_bus")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackEventsProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SlackTextract(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SlackTextract",
):
    '''Extract text from images posted to Slack using Amazon Textract.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        app_id: builtins.str,
        bot_token: _aws_cdk_ceddda9d.SecretValue,
        signing_secret: _aws_cdk_ceddda9d.SecretValue,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param app_id: The application id of the Slack app.
        :param bot_token: The **bot** token of the Slack app. The following scopes are required: ``chat:write`` and ``files:read``
        :param signing_secret: The signing secret of the Slack app.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5412fafbfa9db3ace151f8531d8d91c80847eba6b8a2a7fc7ee406114ad926c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SlackTextractProps(
            app_id=app_id, bot_token=bot_token, signing_secret=signing_secret
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.SlackTextractProps",
    jsii_struct_bases=[],
    name_mapping={
        "app_id": "appId",
        "bot_token": "botToken",
        "signing_secret": "signingSecret",
    },
)
class SlackTextractProps:
    def __init__(
        self,
        *,
        app_id: builtins.str,
        bot_token: _aws_cdk_ceddda9d.SecretValue,
        signing_secret: _aws_cdk_ceddda9d.SecretValue,
    ) -> None:
        '''Properties for a SlackTextract.

        :param app_id: The application id of the Slack app.
        :param bot_token: The **bot** token of the Slack app. The following scopes are required: ``chat:write`` and ``files:read``
        :param signing_secret: The signing secret of the Slack app.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09d807b6292a4fd0edf8de0c60fccf3c92821e9d8343be18dcc7745484002944)
            check_type(argname="argument app_id", value=app_id, expected_type=type_hints["app_id"])
            check_type(argname="argument bot_token", value=bot_token, expected_type=type_hints["bot_token"])
            check_type(argname="argument signing_secret", value=signing_secret, expected_type=type_hints["signing_secret"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_id": app_id,
            "bot_token": bot_token,
            "signing_secret": signing_secret,
        }

    @builtins.property
    def app_id(self) -> builtins.str:
        '''The application id of the Slack app.'''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bot_token(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''The **bot** token of the Slack app.

        The following scopes are required: ``chat:write`` and ``files:read``
        '''
        result = self._values.get("bot_token")
        assert result is not None, "Required property 'bot_token' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    @builtins.property
    def signing_secret(self) -> _aws_cdk_ceddda9d.SecretValue:
        '''The signing secret of the Slack app.'''
        result = self._values.get("signing_secret")
        assert result is not None, "Required property 'signing_secret' is missing"
        return typing.cast(_aws_cdk_ceddda9d.SecretValue, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackTextractProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cloudstructs.SlackkAppManifestBotUser",
    jsii_struct_bases=[],
    name_mapping={"display_name": "displayName", "always_online": "alwaysOnline"},
)
class SlackkAppManifestBotUser:
    def __init__(
        self,
        *,
        display_name: builtins.str,
        always_online: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Bot user configuration.

        :param display_name: The display name of the bot user. Maximum length is 80 characters.
        :param always_online: Whether the bot user will always appear to be online. Default: false

        :see: https://api.slack.com/bot-users
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3f1406f5c634591a59ce6cab4888ba9d276b016ea2ae7b3a45562184276d7e0)
            check_type(argname="argument display_name", value=display_name, expected_type=type_hints["display_name"])
            check_type(argname="argument always_online", value=always_online, expected_type=type_hints["always_online"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "display_name": display_name,
        }
        if always_online is not None:
            self._values["always_online"] = always_online

    @builtins.property
    def display_name(self) -> builtins.str:
        '''The display name of the bot user.

        Maximum length is 80 characters.
        '''
        result = self._values.get("display_name")
        assert result is not None, "Required property 'display_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def always_online(self) -> typing.Optional[builtins.bool]:
        '''Whether the bot user will always appear to be online.

        :default: false
        '''
        result = self._values.get("always_online")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SlackkAppManifestBotUser(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SslServerTest(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.SslServerTest",
):
    '''Perform SSL server test for a hostname.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        host: builtins.str,
        alarm_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        minimum_grade: typing.Optional["SslServerTestGrade"] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param host: The hostname to test.
        :param alarm_topic: The topic to which the results must be sent when the grade is below the minimum grade. Default: - a new topic is created
        :param minimum_grade: Minimum grade for the test. The grade is calculated using the worst grade of all endpoints. Used to send the results to an alarm SNS topic. Default: SslServerTestGrade.A_PLUS
        :param schedule: The schedule for the test. Default: - every day
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26b99367596b8cc6ac6dee6ad68205d4938b94b75c3b4b61050a1057ac9535fc)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SslServerTestProps(
            host=host,
            alarm_topic=alarm_topic,
            minimum_grade=minimum_grade,
            schedule=schedule,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="alarmTopic")
    def alarm_topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        '''The topic to which the SSL test results are sent when the grade is below the minimum grade.'''
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, jsii.get(self, "alarmTopic"))


@jsii.enum(jsii_type="cloudstructs.SslServerTestGrade")
class SslServerTestGrade(enum.Enum):
    '''SSL Server test grade.'''

    A_PLUS = "A_PLUS"
    A = "A"
    A_MINUS = "A_MINUS"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"


@jsii.data_type(
    jsii_type="cloudstructs.SslServerTestProps",
    jsii_struct_bases=[],
    name_mapping={
        "host": "host",
        "alarm_topic": "alarmTopic",
        "minimum_grade": "minimumGrade",
        "schedule": "schedule",
    },
)
class SslServerTestProps:
    def __init__(
        self,
        *,
        host: builtins.str,
        alarm_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
        minimum_grade: typing.Optional[SslServerTestGrade] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    ) -> None:
        '''Properties for a SslServerTest.

        :param host: The hostname to test.
        :param alarm_topic: The topic to which the results must be sent when the grade is below the minimum grade. Default: - a new topic is created
        :param minimum_grade: Minimum grade for the test. The grade is calculated using the worst grade of all endpoints. Used to send the results to an alarm SNS topic. Default: SslServerTestGrade.A_PLUS
        :param schedule: The schedule for the test. Default: - every day
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a43c686f7b70a3cbbdd19c19b209179d73aaa7a343df7a85d17003473297e31)
            check_type(argname="argument host", value=host, expected_type=type_hints["host"])
            check_type(argname="argument alarm_topic", value=alarm_topic, expected_type=type_hints["alarm_topic"])
            check_type(argname="argument minimum_grade", value=minimum_grade, expected_type=type_hints["minimum_grade"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "host": host,
        }
        if alarm_topic is not None:
            self._values["alarm_topic"] = alarm_topic
        if minimum_grade is not None:
            self._values["minimum_grade"] = minimum_grade
        if schedule is not None:
            self._values["schedule"] = schedule

    @builtins.property
    def host(self) -> builtins.str:
        '''The hostname to test.'''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alarm_topic(self) -> typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic]:
        '''The topic to which the results must be sent when the grade is below the minimum grade.

        :default: - a new topic is created
        '''
        result = self._values.get("alarm_topic")
        return typing.cast(typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic], result)

    @builtins.property
    def minimum_grade(self) -> typing.Optional[SslServerTestGrade]:
        '''Minimum grade for the test. The grade is calculated using the worst grade of all endpoints.

        Used to send the results to an alarm SNS topic.

        :default: SslServerTestGrade.A_PLUS
        '''
        result = self._values.get("minimum_grade")
        return typing.cast(typing.Optional[SslServerTestGrade], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The schedule for the test.

        :default: - every day
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SslServerTestProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StateMachineCustomResourceProvider(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.StateMachineCustomResourceProvider",
):
    '''A state machine custom resource provider.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        state_machine: IStateMachine,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param state_machine: The state machine.
        :param timeout: Timeout. Default: Duration.minutes(30)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f32a17c5f3582f6063b771bbb8f60890a54aa9b675a45eec7aed740616fb265)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StateMachineCustomResourceProviderProps(
            state_machine=state_machine, timeout=timeout
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="serviceToken")
    def service_token(self) -> builtins.str:
        '''The service token.'''
        return typing.cast(builtins.str, jsii.get(self, "serviceToken"))


@jsii.data_type(
    jsii_type="cloudstructs.StateMachineCustomResourceProviderProps",
    jsii_struct_bases=[],
    name_mapping={"state_machine": "stateMachine", "timeout": "timeout"},
)
class StateMachineCustomResourceProviderProps:
    def __init__(
        self,
        *,
        state_machine: IStateMachine,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    ) -> None:
        '''Properties for a StateMachineCustomResourceProvider.

        :param state_machine: The state machine.
        :param timeout: Timeout. Default: Duration.minutes(30)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a5360253aec96e06cbd22880074544bf5deb655637f1660b684c5ce3c855bdd)
            check_type(argname="argument state_machine", value=state_machine, expected_type=type_hints["state_machine"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "state_machine": state_machine,
        }
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def state_machine(self) -> IStateMachine:
        '''The state machine.'''
        result = self._values.get("state_machine")
        assert result is not None, "Required property 'state_machine' is missing"
        return typing.cast(IStateMachine, result)

    @builtins.property
    def timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Timeout.

        :default: Duration.minutes(30)
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StateMachineCustomResourceProviderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StaticWebsite(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.StaticWebsite",
):
    '''A CloudFront static website hosted on S3.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        backend_configuration: typing.Any = None,
        cache_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ICachePolicy] = None,
        edge_lambdas: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.EdgeLambda, typing.Dict[builtins.str, typing.Any]]]] = None,
        redirects: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_headers_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicy] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: The domain name for this static website.
        :param hosted_zone: The hosted zone where records should be added.
        :param backend_configuration: A backend configuration that will be saved as ``config.json`` in the S3 bucket of the static website. The frontend can query this config by doing ``fetch('/config.json')``.
        :param cache_policy: Cache policy for the default behavior. Default: CachePolicy.CACHING_OPTIMIZED
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - an origin request function that redirects all requests for a path to /index.html
        :param redirects: A list of domain names that should redirect to ``domainName``. Default: - the domain name of the hosted zone
        :param response_headers_policy: Response headers policy for the default behavior. Default: - a new policy is created with best practice security headers
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c6cce44b6a8e2d4fefe372623c811f7e7e92ce467f8e830604203b6e57fafd1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = StaticWebsiteProps(
            domain_name=domain_name,
            hosted_zone=hosted_zone,
            backend_configuration=backend_configuration,
            cache_policy=cache_policy,
            edge_lambdas=edge_lambdas,
            redirects=redirects,
            response_headers_policy=response_headers_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="defaultSecurityHeadersBehavior")
    def default_security_headers_behavior(
        cls,
    ) -> _aws_cdk_aws_cloudfront_ceddda9d.ResponseSecurityHeadersBehavior:  # pyright: ignore [reportGeneralTypeIssues,reportRedeclaration]
        '''Best practice security headers used as default.'''
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.ResponseSecurityHeadersBehavior, jsii.sget(cls, "defaultSecurityHeadersBehavior"))

    @default_security_headers_behavior.setter # type: ignore[no-redef]
    def default_security_headers_behavior(
        cls,
        value: _aws_cdk_aws_cloudfront_ceddda9d.ResponseSecurityHeadersBehavior,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff35a947730004c6e0408e6ec18be077978abf81aaf6d875e50506463132c574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.sset(cls, "defaultSecurityHeadersBehavior", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> _aws_cdk_aws_s3_ceddda9d.Bucket:
        '''The S3 bucket of this static website.'''
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Bucket, jsii.get(self, "bucket"))

    @builtins.property
    @jsii.member(jsii_name="distribution")
    def distribution(self) -> _aws_cdk_aws_cloudfront_ceddda9d.Distribution:
        '''The CloudFront distribution of this static website.'''
        return typing.cast(_aws_cdk_aws_cloudfront_ceddda9d.Distribution, jsii.get(self, "distribution"))


@jsii.data_type(
    jsii_type="cloudstructs.StaticWebsiteProps",
    jsii_struct_bases=[],
    name_mapping={
        "domain_name": "domainName",
        "hosted_zone": "hostedZone",
        "backend_configuration": "backendConfiguration",
        "cache_policy": "cachePolicy",
        "edge_lambdas": "edgeLambdas",
        "redirects": "redirects",
        "response_headers_policy": "responseHeadersPolicy",
    },
)
class StaticWebsiteProps:
    def __init__(
        self,
        *,
        domain_name: builtins.str,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        backend_configuration: typing.Any = None,
        cache_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ICachePolicy] = None,
        edge_lambdas: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.EdgeLambda, typing.Dict[builtins.str, typing.Any]]]] = None,
        redirects: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_headers_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicy] = None,
    ) -> None:
        '''Properties for a StaticWebsite.

        :param domain_name: The domain name for this static website.
        :param hosted_zone: The hosted zone where records should be added.
        :param backend_configuration: A backend configuration that will be saved as ``config.json`` in the S3 bucket of the static website. The frontend can query this config by doing ``fetch('/config.json')``.
        :param cache_policy: Cache policy for the default behavior. Default: CachePolicy.CACHING_OPTIMIZED
        :param edge_lambdas: The Lambda@Edge functions to invoke before serving the contents. Default: - an origin request function that redirects all requests for a path to /index.html
        :param redirects: A list of domain names that should redirect to ``domainName``. Default: - the domain name of the hosted zone
        :param response_headers_policy: Response headers policy for the default behavior. Default: - a new policy is created with best practice security headers
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4daf76d01dee77dafb229e369b86df1b96ef0477a43bf4df595b7453b0e74392)
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument backend_configuration", value=backend_configuration, expected_type=type_hints["backend_configuration"])
            check_type(argname="argument cache_policy", value=cache_policy, expected_type=type_hints["cache_policy"])
            check_type(argname="argument edge_lambdas", value=edge_lambdas, expected_type=type_hints["edge_lambdas"])
            check_type(argname="argument redirects", value=redirects, expected_type=type_hints["redirects"])
            check_type(argname="argument response_headers_policy", value=response_headers_policy, expected_type=type_hints["response_headers_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_name": domain_name,
            "hosted_zone": hosted_zone,
        }
        if backend_configuration is not None:
            self._values["backend_configuration"] = backend_configuration
        if cache_policy is not None:
            self._values["cache_policy"] = cache_policy
        if edge_lambdas is not None:
            self._values["edge_lambdas"] = edge_lambdas
        if redirects is not None:
            self._values["redirects"] = redirects
        if response_headers_policy is not None:
            self._values["response_headers_policy"] = response_headers_policy

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''The domain name for this static website.

        Example::

            www.my-static-website.com
        '''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone where records should be added.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    @builtins.property
    def backend_configuration(self) -> typing.Any:
        '''A backend configuration that will be saved as ``config.json`` in the S3 bucket of the static website.

        The frontend can query this config by doing ``fetch('/config.json')``.

        Example::

            { userPoolId: '1234', apiEndoint: 'https://www.my-api.com/api' }
        '''
        result = self._values.get("backend_configuration")
        return typing.cast(typing.Any, result)

    @builtins.property
    def cache_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ICachePolicy]:
        '''Cache policy for the default behavior.

        :default: CachePolicy.CACHING_OPTIMIZED
        '''
        result = self._values.get("cache_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ICachePolicy], result)

    @builtins.property
    def edge_lambdas(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_cloudfront_ceddda9d.EdgeLambda]]:
        '''The Lambda@Edge functions to invoke before serving the contents.

        :default: - an origin request function that redirects all requests for a path to /index.html
        '''
        result = self._values.get("edge_lambdas")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_cloudfront_ceddda9d.EdgeLambda]], result)

    @builtins.property
    def redirects(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of domain names that should redirect to ``domainName``.

        :default: - the domain name of the hosted zone
        '''
        result = self._values.get("redirects")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def response_headers_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicy]:
        '''Response headers policy for the default behavior.

        :default: - a new policy is created with best practice security headers
        '''
        result = self._values.get("response_headers_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicy], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StaticWebsiteProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ToolkitCleaner(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.ToolkitCleaner",
):
    '''Clean unused S3 and ECR assets from your CDK Toolkit.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        clean_assets_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        dry_run: typing.Optional[builtins.bool] = None,
        retain_assets_newer_than: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        schedule_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param clean_assets_timeout: The timeout for the Lambda functions that clean assets. Default: Duration.minutes(5)
        :param dry_run: Only output number of assets and total size that would be deleted but without actually deleting assets.
        :param retain_assets_newer_than: Retain unused assets that were created recently. Default: - all unused assets are removed
        :param schedule: The schedule for the cleaner. Default: - every day
        :param schedule_enabled: Whether to clean on schedule. If you'd like to run the cleanup manually via the console, set to ``false``. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00fb1018addaa6fbbee6e44dc96b9421d79e37fba0a61f552b58d39e4f614888)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = ToolkitCleanerProps(
            clean_assets_timeout=clean_assets_timeout,
            dry_run=dry_run,
            retain_assets_newer_than=retain_assets_newer_than,
            schedule=schedule,
            schedule_enabled=schedule_enabled,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cloudstructs.ToolkitCleanerProps",
    jsii_struct_bases=[],
    name_mapping={
        "clean_assets_timeout": "cleanAssetsTimeout",
        "dry_run": "dryRun",
        "retain_assets_newer_than": "retainAssetsNewerThan",
        "schedule": "schedule",
        "schedule_enabled": "scheduleEnabled",
    },
)
class ToolkitCleanerProps:
    def __init__(
        self,
        *,
        clean_assets_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        dry_run: typing.Optional[builtins.bool] = None,
        retain_assets_newer_than: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
        schedule_enabled: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''Properties for a ToolkitCleaner.

        :param clean_assets_timeout: The timeout for the Lambda functions that clean assets. Default: Duration.minutes(5)
        :param dry_run: Only output number of assets and total size that would be deleted but without actually deleting assets.
        :param retain_assets_newer_than: Retain unused assets that were created recently. Default: - all unused assets are removed
        :param schedule: The schedule for the cleaner. Default: - every day
        :param schedule_enabled: Whether to clean on schedule. If you'd like to run the cleanup manually via the console, set to ``false``. Default: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a9c40653a5bdf69499b5627cdaf6eb4c23945c6111027ebe1d6a9b524f87d3)
            check_type(argname="argument clean_assets_timeout", value=clean_assets_timeout, expected_type=type_hints["clean_assets_timeout"])
            check_type(argname="argument dry_run", value=dry_run, expected_type=type_hints["dry_run"])
            check_type(argname="argument retain_assets_newer_than", value=retain_assets_newer_than, expected_type=type_hints["retain_assets_newer_than"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument schedule_enabled", value=schedule_enabled, expected_type=type_hints["schedule_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if clean_assets_timeout is not None:
            self._values["clean_assets_timeout"] = clean_assets_timeout
        if dry_run is not None:
            self._values["dry_run"] = dry_run
        if retain_assets_newer_than is not None:
            self._values["retain_assets_newer_than"] = retain_assets_newer_than
        if schedule is not None:
            self._values["schedule"] = schedule
        if schedule_enabled is not None:
            self._values["schedule_enabled"] = schedule_enabled

    @builtins.property
    def clean_assets_timeout(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''The timeout for the Lambda functions that clean assets.

        :default: Duration.minutes(5)
        '''
        result = self._values.get("clean_assets_timeout")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def dry_run(self) -> typing.Optional[builtins.bool]:
        '''Only output number of assets and total size that would be deleted but without actually deleting assets.'''
        result = self._values.get("dry_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def retain_assets_newer_than(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Retain unused assets that were created recently.

        :default: - all unused assets are removed
        '''
        result = self._values.get("retain_assets_newer_than")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def schedule(self) -> typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule]:
        '''The schedule for the cleaner.

        :default: - every day
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule], result)

    @builtins.property
    def schedule_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether to clean on schedule.

        If you'd like to run the cleanup manually
        via the console, set to ``false``.

        :default: true
        '''
        result = self._values.get("schedule_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ToolkitCleanerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class UrlShortener(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cloudstructs.UrlShortener",
):
    '''URL shortener.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        api_gateway_authorizer: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAuthorizer] = None,
        api_gateway_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors_allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        iam_authorization: typing.Optional[builtins.bool] = None,
        record_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: The hosted zone for the short URLs domain.
        :param api_gateway_authorizer: Authorizer for API gateway. Default: - do not use an authorizer for the API
        :param api_gateway_endpoint: An interface VPC endpoint for API gateway. Specifying this property will make the API private. Default: - API is public
        :param bucket_name: A name for the bucket saving the redirects. Default: - derived from short link domain name
        :param cors_allow_origins: Allowed origins for CORS. Default: - CORS is not enabled
        :param expiration: Expiration for short urls. Default: cdk.Duration.days(365)
        :param iam_authorization: Whether to use IAM authorization. Default: - do not use IAM authorization
        :param record_name: The record name to use in the hosted zone. Default: - zone root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__167f33600ab96baf2049b3f60519f5b2752e085a16e7fb198ede85d7e14b868c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = UrlShortenerProps(
            hosted_zone=hosted_zone,
            api_gateway_authorizer=api_gateway_authorizer,
            api_gateway_endpoint=api_gateway_endpoint,
            bucket_name=bucket_name,
            cors_allow_origins=cors_allow_origins,
            expiration=expiration,
            iam_authorization=iam_authorization,
            record_name=record_name,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''Grant access to invoke the URL shortener if protected by IAM authorization.

        :param grantee: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46a7eb08de5218cee5cd8528a6e312f96935b2aa46d50090cf09844b564b8a27)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="api")
    def api(self) -> _aws_cdk_aws_apigateway_ceddda9d.RestApi:
        '''The underlying API Gateway REST API.'''
        return typing.cast(_aws_cdk_aws_apigateway_ceddda9d.RestApi, jsii.get(self, "api"))

    @builtins.property
    @jsii.member(jsii_name="apiEndpoint")
    def api_endpoint(self) -> builtins.str:
        '''The endpoint of the URL shortener API.'''
        return typing.cast(builtins.str, jsii.get(self, "apiEndpoint"))


@jsii.data_type(
    jsii_type="cloudstructs.UrlShortenerProps",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "api_gateway_authorizer": "apiGatewayAuthorizer",
        "api_gateway_endpoint": "apiGatewayEndpoint",
        "bucket_name": "bucketName",
        "cors_allow_origins": "corsAllowOrigins",
        "expiration": "expiration",
        "iam_authorization": "iamAuthorization",
        "record_name": "recordName",
    },
)
class UrlShortenerProps:
    def __init__(
        self,
        *,
        hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        api_gateway_authorizer: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAuthorizer] = None,
        api_gateway_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors_allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
        expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        iam_authorization: typing.Optional[builtins.bool] = None,
        record_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Properties for a UrlShortener.

        :param hosted_zone: The hosted zone for the short URLs domain.
        :param api_gateway_authorizer: Authorizer for API gateway. Default: - do not use an authorizer for the API
        :param api_gateway_endpoint: An interface VPC endpoint for API gateway. Specifying this property will make the API private. Default: - API is public
        :param bucket_name: A name for the bucket saving the redirects. Default: - derived from short link domain name
        :param cors_allow_origins: Allowed origins for CORS. Default: - CORS is not enabled
        :param expiration: Expiration for short urls. Default: cdk.Duration.days(365)
        :param iam_authorization: Whether to use IAM authorization. Default: - do not use IAM authorization
        :param record_name: The record name to use in the hosted zone. Default: - zone root
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e3b7727492b636232f327e92ab8db610427777b8176a1c90738cf41ebadf9e8)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument api_gateway_authorizer", value=api_gateway_authorizer, expected_type=type_hints["api_gateway_authorizer"])
            check_type(argname="argument api_gateway_endpoint", value=api_gateway_endpoint, expected_type=type_hints["api_gateway_endpoint"])
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument cors_allow_origins", value=cors_allow_origins, expected_type=type_hints["cors_allow_origins"])
            check_type(argname="argument expiration", value=expiration, expected_type=type_hints["expiration"])
            check_type(argname="argument iam_authorization", value=iam_authorization, expected_type=type_hints["iam_authorization"])
            check_type(argname="argument record_name", value=record_name, expected_type=type_hints["record_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone": hosted_zone,
        }
        if api_gateway_authorizer is not None:
            self._values["api_gateway_authorizer"] = api_gateway_authorizer
        if api_gateway_endpoint is not None:
            self._values["api_gateway_endpoint"] = api_gateway_endpoint
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if cors_allow_origins is not None:
            self._values["cors_allow_origins"] = cors_allow_origins
        if expiration is not None:
            self._values["expiration"] = expiration
        if iam_authorization is not None:
            self._values["iam_authorization"] = iam_authorization
        if record_name is not None:
            self._values["record_name"] = record_name

    @builtins.property
    def hosted_zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        '''The hosted zone for the short URLs domain.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    @builtins.property
    def api_gateway_authorizer(
        self,
    ) -> typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAuthorizer]:
        '''Authorizer for API gateway.

        :default: - do not use an authorizer for the API
        '''
        result = self._values.get("api_gateway_authorizer")
        return typing.cast(typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAuthorizer], result)

    @builtins.property
    def api_gateway_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint]:
        '''An interface VPC endpoint for API gateway.

        Specifying this property will
        make the API private.

        :default: - API is public

        :see: https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-private-apis.html
        '''
        result = self._values.get("api_gateway_endpoint")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint], result)

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''A name for the bucket saving the redirects.

        :default: - derived from short link domain name
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cors_allow_origins(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Allowed origins for CORS.

        :default: - CORS is not enabled
        '''
        result = self._values.get("cors_allow_origins")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def expiration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''Expiration for short urls.

        :default: cdk.Duration.days(365)
        '''
        result = self._values.get("expiration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def iam_authorization(self) -> typing.Optional[builtins.bool]:
        '''Whether to use IAM authorization.

        :default: - do not use IAM authorization
        '''
        result = self._values.get("iam_authorization")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def record_name(self) -> typing.Optional[builtins.str]:
        '''The record name to use in the hosted zone.

        :default: - zone root
        '''
        result = self._values.get("record_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UrlShortenerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CodeCommitMirror",
    "CodeCommitMirrorProps",
    "CodeCommitMirrorSourceRepository",
    "DmarcAlignment",
    "DmarcPolicy",
    "DmarcReporter",
    "DmarcReporterProps",
    "EcsServiceRoller",
    "EcsServiceRollerProps",
    "EmailReceiver",
    "EmailReceiverProps",
    "IStateMachine",
    "MjmlTemplate",
    "MjmlTemplateProps",
    "RollTrigger",
    "SamlFederatedPrincipal",
    "SamlIdentityProvider",
    "SamlIdentityProviderProps",
    "SlackApp",
    "SlackAppManifest",
    "SlackAppManifestAppHome",
    "SlackAppManifestDefinition",
    "SlackAppManifestEventSubscriptions",
    "SlackAppManifestInteractivity",
    "SlackAppManifestOauthConfig",
    "SlackAppManifestProps",
    "SlackAppManifestSettings",
    "SlackAppManifestShortcut",
    "SlackAppManifestShortcutType",
    "SlackAppManifestSlashCommand",
    "SlackAppManifestWorkflowStep",
    "SlackAppProps",
    "SlackEvents",
    "SlackEventsProps",
    "SlackTextract",
    "SlackTextractProps",
    "SlackkAppManifestBotUser",
    "SslServerTest",
    "SslServerTestGrade",
    "SslServerTestProps",
    "StateMachineCustomResourceProvider",
    "StateMachineCustomResourceProviderProps",
    "StaticWebsite",
    "StaticWebsiteProps",
    "ToolkitCleaner",
    "ToolkitCleanerProps",
    "UrlShortener",
    "UrlShortenerProps",
]

publication.publish()

def _typecheckingstub__775d0a2a4ad4d1672c6555b5fea4da6dc7435ddea6c63db13b79d587651e13c1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    repository: CodeCommitMirrorSourceRepository,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea93461a0d56e64ddfee27f76a8f585e8ab317fa994825218d03706d0684ec6b(
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    repository: CodeCommitMirrorSourceRepository,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09f67e4d4aeae1f0358e343cd060bc1a176ef8adf4a4b5c49a3b8216aa4f0c5b(
    owner: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9c5ea96c99b4d98cccb560282863340d507a7bea06dd48c633374937c378a51(
    name: builtins.str,
    url: _aws_cdk_aws_ecs_ceddda9d.Secret,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01bd02e34cc162be822e89501c85ac44ba576832ec13dfbe18c7d3f48c6caa7f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    dmarc_policy: DmarcPolicy,
    function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
    additional_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
    dmarc_dkim_alignment: typing.Optional[DmarcAlignment] = None,
    dmarc_percentage: typing.Optional[jsii.Number] = None,
    dmarc_spf_alignment: typing.Optional[DmarcAlignment] = None,
    dmarc_subdomain_policy: typing.Optional[DmarcPolicy] = None,
    email_address: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8808781a101fae34a67aa2c6db024d6ac63f2f0c2584452a348244b8a7c0b728(
    *,
    dmarc_policy: DmarcPolicy,
    function: _aws_cdk_aws_lambda_ceddda9d.IFunction,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
    additional_email_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
    after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
    dmarc_dkim_alignment: typing.Optional[DmarcAlignment] = None,
    dmarc_percentage: typing.Optional[jsii.Number] = None,
    dmarc_spf_alignment: typing.Optional[DmarcAlignment] = None,
    dmarc_subdomain_policy: typing.Optional[DmarcPolicy] = None,
    email_address: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__753ff7415ecea63b65291ecfbbe3c3309a1a616b70c4b0fbba3ebeb929a13136(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    service: _aws_cdk_aws_ecs_ceddda9d.IService,
    trigger: typing.Optional[RollTrigger] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c382475ffeab1ce7e285837dbf808dbf36902533fcd860db3d3ecfffe47388f(
    *,
    cluster: _aws_cdk_aws_ecs_ceddda9d.ICluster,
    service: _aws_cdk_aws_ecs_ceddda9d.IService,
    trigger: typing.Optional[RollTrigger] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2b6712707b39b2d133dd62aef1ea71cf3732c305783f22f76cbafc80508bcaf(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
    recipients: typing.Sequence[builtins.str],
    after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
    enabled: typing.Optional[builtins.bool] = None,
    function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    source_whitelist: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8500959d1e20d8ab966122bf508b686ba123767348a2c264cc34f3ce69165ae2(
    *,
    receipt_rule_set: _aws_cdk_aws_ses_ceddda9d.IReceiptRuleSet,
    recipients: typing.Sequence[builtins.str],
    after_rule: typing.Optional[_aws_cdk_aws_ses_ceddda9d.IReceiptRule] = None,
    enabled: typing.Optional[builtins.bool] = None,
    function: typing.Optional[_aws_cdk_aws_lambda_ceddda9d.IFunction] = None,
    source_whitelist: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c14fd1220e2b1a369a0a4b700ec2fd623089a00de406d691f1ebd18fbe576b9(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    mjml: builtins.str,
    subject: builtins.str,
    template_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__702b570f1be82d9279663f13742ac81b522b758421dbf6217639f90302a51319(
    *,
    mjml: builtins.str,
    subject: builtins.str,
    template_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04afa5cfc7c8bd76ded88022a29c6aea3d843c1b85acbd7eee9cf5e3d5f838a6(
    rule: _aws_cdk_aws_events_ceddda9d.Rule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0deaf527c94f861e7ddb946f9577b690fc63af2396d1fc1e60144369fbc9f1cf(
    schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52a6b959b946204571517a06c24aa681e69d738ec4d7c40fba77a491cc458c59(
    identity_provider: SamlIdentityProvider,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a951b64d20b1aeea237a4b8d92c7fdf172eac09779a2608ad7de3f809f4eaa13(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    metadata_document: builtins.str,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f9fcdf914a540045500dda8934754c0881bc068d0e619a7a76f6379fb77e9d4(
    *,
    metadata_document: builtins.str,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__465b057c57a03fb90832edc94826ab9fb04f18aca74f9db74978e3764dda2d61(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    configuration_token_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    manifest: SlackAppManifestDefinition,
    credentials_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c292ea7dcd606ba7b5b1c30bd9f20d3c9e3a97b2fd901078fbde4ee5d4141f98(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebc564e9f94fc31e05482aae2aea3411ba92076e3c728589a206f8a9d9da9fc1(
    *,
    home_tab: typing.Optional[builtins.bool] = None,
    messages_tab: typing.Optional[builtins.bool] = None,
    messages_tab_read_only: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9861cffdd6158b4e677b4da06928ef6a7b9bd623beacbc39060fc371dae6df2d(
    file: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__442948d30bfd13d2eb21cb8bfe977e866d481c4426e25e028a24219a78a44451(
    manifest: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33c88afd12de1290db0923503493054b4d8e13085afa9cbb8c4185f83aaa951c(
    construct: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f760e51128fe54d75e4283960678989fab49ecddde79deec8d2aab9b20e430d7(
    *,
    request_url: builtins.str,
    bot_events: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_events: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e58235c45e7590fe9814bb419867acbcd4af8fc1b7f672d36385a0c7a6a1df3b(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    message_menu_options_url: typing.Optional[builtins.str] = None,
    request_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a4285b701f803583267e7d3fabf4f0d5927a0963c2907bb137ad64fd34321c5(
    *,
    bot_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    redirect_urls: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74c65eb0c2898e68978843e3401e2c4a6e49e561b964c1b7179ecbe9546b2022(
    *,
    name: builtins.str,
    allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    app_home: typing.Optional[typing.Union[SlackAppManifestAppHome, typing.Dict[builtins.str, typing.Any]]] = None,
    background_color: typing.Optional[builtins.str] = None,
    bot_user: typing.Optional[typing.Union[SlackkAppManifestBotUser, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    event_subscriptions: typing.Optional[typing.Union[SlackAppManifestEventSubscriptions, typing.Dict[builtins.str, typing.Any]]] = None,
    interactivity: typing.Optional[typing.Union[SlackAppManifestInteractivity, typing.Dict[builtins.str, typing.Any]]] = None,
    long_description: typing.Optional[builtins.str] = None,
    major_version: typing.Optional[jsii.Number] = None,
    minor_version: typing.Optional[jsii.Number] = None,
    oauth_config: typing.Optional[typing.Union[SlackAppManifestOauthConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    org_deploy: typing.Optional[builtins.bool] = None,
    shortcuts: typing.Optional[typing.Sequence[typing.Union[SlackAppManifestShortcut, typing.Dict[builtins.str, typing.Any]]]] = None,
    slash_commands: typing.Optional[typing.Sequence[typing.Union[SlackAppManifestSlashCommand, typing.Dict[builtins.str, typing.Any]]]] = None,
    socket_mode: typing.Optional[builtins.bool] = None,
    unfurl_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    workflow_steps: typing.Optional[typing.Sequence[typing.Union[SlackAppManifestWorkflowStep, typing.Dict[builtins.str, typing.Any]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae6cef8f97993e8837c36e28365e7d270ee7de63f7ad8a03151bf8157d3c9a9b(
    *,
    allowed_ip_address_ranges: typing.Optional[typing.Sequence[builtins.str]] = None,
    event_subscriptions: typing.Optional[typing.Union[SlackAppManifestEventSubscriptions, typing.Dict[builtins.str, typing.Any]]] = None,
    interactivity: typing.Optional[typing.Union[SlackAppManifestInteractivity, typing.Dict[builtins.str, typing.Any]]] = None,
    org_deploy: typing.Optional[builtins.bool] = None,
    socket_mode: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b511717247813827d96471269da9620f5038467fcb8c7f43381dac0722dd0030(
    *,
    callback_id: builtins.str,
    description: builtins.str,
    name: builtins.str,
    type: SlackAppManifestShortcutType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3b48421ebf37a276ebe1a2f9723f99362dbf35cdb7f2acb57844b6dc6f1611f(
    *,
    command: builtins.str,
    description: builtins.str,
    should_escape: typing.Optional[builtins.bool] = None,
    url: typing.Optional[builtins.str] = None,
    usage_hint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72e624e96c2a7571173b90657cfb84ff239679796527e8155c83f02352f63849(
    *,
    callback_id: builtins.str,
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8dd6d3b3477e298be57433e7c12f534278e17d0927c136b7cb0d32ecfc05a8d(
    *,
    configuration_token_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    manifest: SlackAppManifestDefinition,
    credentials_secret: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.ISecret] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__712a11486ef4ddd0a37ce4f4c6116743132220a3f83a522d69417bf554327c80(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    signing_secret: _aws_cdk_ceddda9d.SecretValue,
    api_name: typing.Optional[builtins.str] = None,
    custom_event_bus: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__844db98a7fefe45c6d2e05f3b5c81e4e0a5cb3f865f4c32b4622a66121d2bb89(
    *,
    signing_secret: _aws_cdk_ceddda9d.SecretValue,
    api_name: typing.Optional[builtins.str] = None,
    custom_event_bus: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5412fafbfa9db3ace151f8531d8d91c80847eba6b8a2a7fc7ee406114ad926c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    app_id: builtins.str,
    bot_token: _aws_cdk_ceddda9d.SecretValue,
    signing_secret: _aws_cdk_ceddda9d.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09d807b6292a4fd0edf8de0c60fccf3c92821e9d8343be18dcc7745484002944(
    *,
    app_id: builtins.str,
    bot_token: _aws_cdk_ceddda9d.SecretValue,
    signing_secret: _aws_cdk_ceddda9d.SecretValue,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3f1406f5c634591a59ce6cab4888ba9d276b016ea2ae7b3a45562184276d7e0(
    *,
    display_name: builtins.str,
    always_online: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26b99367596b8cc6ac6dee6ad68205d4938b94b75c3b4b61050a1057ac9535fc(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    host: builtins.str,
    alarm_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    minimum_grade: typing.Optional[SslServerTestGrade] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a43c686f7b70a3cbbdd19c19b209179d73aaa7a343df7a85d17003473297e31(
    *,
    host: builtins.str,
    alarm_topic: typing.Optional[_aws_cdk_aws_sns_ceddda9d.ITopic] = None,
    minimum_grade: typing.Optional[SslServerTestGrade] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f32a17c5f3582f6063b771bbb8f60890a54aa9b675a45eec7aed740616fb265(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    state_machine: IStateMachine,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a5360253aec96e06cbd22880074544bf5deb655637f1660b684c5ce3c855bdd(
    *,
    state_machine: IStateMachine,
    timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c6cce44b6a8e2d4fefe372623c811f7e7e92ce467f8e830604203b6e57fafd1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: builtins.str,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    backend_configuration: typing.Any = None,
    cache_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ICachePolicy] = None,
    edge_lambdas: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.EdgeLambda, typing.Dict[builtins.str, typing.Any]]]] = None,
    redirects: typing.Optional[typing.Sequence[builtins.str]] = None,
    response_headers_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff35a947730004c6e0408e6ec18be077978abf81aaf6d875e50506463132c574(
    value: _aws_cdk_aws_cloudfront_ceddda9d.ResponseSecurityHeadersBehavior,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4daf76d01dee77dafb229e369b86df1b96ef0477a43bf4df595b7453b0e74392(
    *,
    domain_name: builtins.str,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    backend_configuration: typing.Any = None,
    cache_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ICachePolicy] = None,
    edge_lambdas: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.EdgeLambda, typing.Dict[builtins.str, typing.Any]]]] = None,
    redirects: typing.Optional[typing.Sequence[builtins.str]] = None,
    response_headers_policy: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.ResponseHeadersPolicy] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00fb1018addaa6fbbee6e44dc96b9421d79e37fba0a61f552b58d39e4f614888(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    clean_assets_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    dry_run: typing.Optional[builtins.bool] = None,
    retain_assets_newer_than: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    schedule_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a9c40653a5bdf69499b5627cdaf6eb4c23945c6111027ebe1d6a9b524f87d3(
    *,
    clean_assets_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    dry_run: typing.Optional[builtins.bool] = None,
    retain_assets_newer_than: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    schedule: typing.Optional[_aws_cdk_aws_events_ceddda9d.Schedule] = None,
    schedule_enabled: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__167f33600ab96baf2049b3f60519f5b2752e085a16e7fb198ede85d7e14b868c(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    api_gateway_authorizer: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAuthorizer] = None,
    api_gateway_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors_allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
    expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    iam_authorization: typing.Optional[builtins.bool] = None,
    record_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46a7eb08de5218cee5cd8528a6e312f96935b2aa46d50090cf09844b564b8a27(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e3b7727492b636232f327e92ab8db610427777b8176a1c90738cf41ebadf9e8(
    *,
    hosted_zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    api_gateway_authorizer: typing.Optional[_aws_cdk_aws_apigateway_ceddda9d.IAuthorizer] = None,
    api_gateway_endpoint: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IInterfaceVpcEndpoint] = None,
    bucket_name: typing.Optional[builtins.str] = None,
    cors_allow_origins: typing.Optional[typing.Sequence[builtins.str]] = None,
    expiration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    iam_authorization: typing.Optional[builtins.bool] = None,
    record_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
