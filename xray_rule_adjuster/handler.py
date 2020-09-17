import json, os
import boto3

xray = boto3.client('xray')
XRAY_RULE_ARN = os.environ['XRAY_RULE_ARN']

def lambda_handler(event, context):
    alarm_state = get_alarm_state(event)
    if alarm_state == 'ALARM':
        # Sets 15 requests/sec + fixed rate 10%
        adjust_sampling_rate(fixed_rate=0.1, resevoir_size=15)
    elif alarm_state == 'OK':
        # Sets 1 requests/sec + fixed rate 5%
        adjust_sampling_rate(fixed_rate=0.05, resevoir_size=1)
        
def get_alarm_state(event):
    alarm_state = 'INSUFFICIENT_DATA'
    records = event.get('Records', [])
    if records:
        alarm_state = json.loads(records[0]['Sns']['Message'])['NewStateValue']
        
    return alarm_state
    
def adjust_sampling_rate(fixed_rate, resevoir_size):
    xray.update_sampling_rule(
        SamplingRuleUpdate={
            'RuleARN': XRAY_RULE_ARN,
            'FixedRate': fixed_rate, 
            'ReservoirSize': resevoir_size
        }
    )