import boto3
import os, json
from random import random

xray = boto3.client('xray')
XRAY_RULE_ARN = os.environ['XRAY_RULE_ARN']

def lambda_handler(event, context):
    success = True
    rule = get_api_sampling_rule()
    iserror='false'
    try:
        iserror=event['queryStringParameters']['error']
    except:
        print("shh.. do not tell anyone!!")
        
    if iserror == 'true':
        success = False

    return {
        # fail the request randomly to trigger X-Ray rule adjustment
        "statusCode": 200 if success else 500,
        "body": json.dumps({
            "Success" : success,
            # return the rule definition to the response
            "SamplingRule": rule
        }, indent=2)
    }

def get_api_sampling_rule():
    response = xray.get_sampling_rules()
    rules = response.get('SamplingRuleRecords', [])
    for r in rules:
        rule = r.get('SamplingRule', {})
        if rule.get('RuleARN', '') == XRAY_RULE_ARN:
            return rule

    return None
