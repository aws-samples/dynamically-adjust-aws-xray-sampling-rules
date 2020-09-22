## Dynamically adjust sampling rules in X-Ray
This repo is used in the AWS blog (https://aws.amazon.com/blogs/mt/dynamically-adjusting-x-ray-sampling-rules/) to showcase dynamic sampling rules on X-Ray 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.


## Architecture
Generic pattern of dynamic sampling rule adjustment is shown below. The idea is to use CloudWatch alarm to trigger the X-Ray sampling rule 
adjustment process. The alarm can be configured based on applications needs, for example high CPU utilization, number of Lambda function failures, 
or rate of 5xx errors in API Gateway.

![Pattern](/doc/pattern.png)

This pattern can be applied to a number of architectures. This repository illustrates it using a simple web application that 
contains of API Gateway and backend Lambda function. 

![Architecture](/doc/architecture.png)

1. Clients access API Gateway using HTTP requests
2. API Gateway forwards requests to AWS Lambda function for processing
3. Errors in lambda function trigger CloudWatch alarm state change
4. Message about changed alarm state is posted in SNS topic
5. Lambda function is triggered in response to SNS message
6. Based on Alarm state, X-Ray sampling rules are adjusted
7. Incoming requests are traced based on updated rules

## Build and deploy instructions
Example template provided uses [AWS SAM](https://aws.amazon.com/serverless/sam/) to simplify the deployment.

To install lambda function dependencies and create a deployment package use the following command:
```
sam build
```

Once the project is built, use [sam deploy](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-cli-command-reference-sam-deploy.html)
to deploy the stack:

```
sam deploy --guided
```

or by providing all parameters in command line:

```
sam deploy --stack-name <stack-name> --s3-bucket <deployment-bucket> --capabilities CAPABILITY_IAM
```

Use the `WebApi` output value to access the deployed API:
```
CloudFormation outputs from deployed stack
-----------------------------------------------------------------------------------
Outputs
-----------------------------------------------------------------------------------
Key                 WebApi
Description         API Gateway endpoint URL for Prod stage for WebApi function
Value               https://xxxxxxxxxx.execute-api.eu-west-1.amazonaws.com/Prod/
-----------------------------------------------------------------------------------
```

## X-Ray sampling rule custom resource properties
The repository demonstrates how to manage AWS X-Ray sampling rule resources
using CloudFormation. At the time of writing there is no standard resource type
you can use, so a custom implementation is needed.

The implementation relies on [Custom Resource Helper](https://github.com/aws-cloudformation/custom-resource-helper) package. 


| Name | Type | Required | Default | Description |
| --- | ---| --- | ---| --- |
| `Name` | string | yes | | Name of the sampling rule |
| `Priority` | int | yes | | Must be from the range of 1-9999 |
| `FixedRate` | float | yes | | Must be from the range of 0-1 |
| `ReservoirSize` | int | yes | | Maximum number of request to sample per second |
| `ResourceARN`  | string | no | * | Resource ARN to match |
| `ServiceName`  | string | no | * | Name of the service to match |
| `ServiceType`  | string | no | * | Type of the service to match |
| `Host`  | string | no | * | The IP address or EC2 hostname to match |
| `HTTPMethod`  | string | no | * | HTTP method to match |
| `URLPath`  | string | no | * | URL path to match |


## Custom Resource return values

Return values can be referenced in CloudFormation template using [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html)

| Name | Description |
| --- | --- |
| `Name`  | Name of the sampling rule |
| `Arn`  | ARN of the sampling rule |