from crhelper import CfnResource
import logging
import boto3
import re
import os

# Initialise the helper, all inputs are optional, this example shows the defaults
helper = CfnResource(json_logging=False, log_level='DEBUG', boto_level='CRITICAL', sleep_on_delete=120)

try:
    # Init code goes here
    client = boto3.client('xray')
    logger = logging.getLogger(__name__)
except Exception as e:
    helper.init_failure(e)


@helper.create
def create(event, context):
    # Optionally return an ID that will be used for the resource PhysicalResourceId, 
    # if None is returned an ID will be generated. If a poll_create function is defined 
    # return value is placed into the poll event as event['CrHelperData']['PhysicalResourceId']

    config = create_configuration(event)
    config['Version'] = 1

    response = client.create_sampling_rule(SamplingRule=config)
    return setup_resource_properties_and_return_arn(response)


@helper.update
def update(event, context):
    # If the update resulted in a new resource being created, return an id for the new resource. 
    # CloudFormation will send a delete event with the old id when stack update completes

    arn = event['PhysicalResourceId']
    original_name = deserialize_sampling_rule_name(arn)
    new_name = event['ResourceProperties']['Name']

    # handle change of the sampling rule's name by creating a new one (name is immutable)
    if original_name != new_name:
        return create(event, context)

    config = create_configuration(event)  
    response = client.update_sampling_rule(SamplingRuleUpdate=config)
    setup_resource_properties_and_return_arn(response)


@helper.delete
def delete(event, context):
    # Delete never returns anything. Should not fail if the underlying resources are already deleted.
    arn = event['PhysicalResourceId']
    client.delete_sampling_rule(RuleARN=arn)


def setup_resource_properties_and_return_arn(response):
    arn = response['SamplingRuleRecord']['SamplingRule']['RuleARN']
    name = response['SamplingRuleRecord']['SamplingRule']['RuleName']

    helper.Data["Arn"] = arn
    helper.Data["Name"] = name
    return arn


def create_configuration(event):
    props = event['ResourceProperties']
    
    return {
        # required properties
        'RuleName': props['Name'],
        'Priority': int(props['Priority']),
        'FixedRate': float(props['FixedRate']),
        'ReservoirSize': int(props['ReservoirSize']),
        # optional properties
        'ResourceARN': props.get('ResourceARN', '*'),
        'ServiceName': props.get('ServiceName', '*'),
        'ServiceType': props.get('ServiceType', '*'),
        'Host':        props.get('Host', '*'),
        'HTTPMethod':  props.get('HTTPMethod', '*'),
        'URLPath':     props.get('URLPath', '*')
    }


def deserialize_sampling_rule_name(physical_id):
    # parse sampling rule name from ARN
    pattern = r'^.+?:.+?:.+?:.+?:.+?:sampling-rule\/(.+?)$'

    match = re.search(pattern, physical_id)
    if match: 
        return match.group(1)
    
    raise ValueError("Invalid sampling rule ARN!")


def lambda_handler(event, context):
    helper(event, context)
