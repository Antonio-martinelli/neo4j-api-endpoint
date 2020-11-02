# Neo4j API Endpoint

The goal of this project is to build a solution using Serverless Framework to offer an API endpoint on AWS that lets a user query a Neo4j database sending a symmetrical encrypted JWT including the database name.

![Workflow](images/workflow.png?raw=true "Workflow")

The user is requested to send a JWT encrypted message storing the database name to be queried to the API Gateway.

The Gateway will invoke a Lambda that will use the private key copy stored on SSM to attempt decryption and read the content of the request.

If the database name is found, the Lambda will connect to Neo4j and, if the database exists, will return the execution of the cypher query `MATCH (n) RETURN COUNT(n) AS num` to the client.

Many checks are run on the request:

* if JWT is not present in the "headers", code 412 is returned;
* if JWT is tampered, code 401 is returned;
* if database is not present in decrypted JWT, code 412 is returned;
* if database is unreachable, code 500 is returned;
* if the requested database does not exist, code 404 is returned.

If all the checks are passed, the result of the query is returned in the body of the response.

Every result is logged to CloudWatch, and an alert has been manually configured for easiness, related to concurrent executions: a message would be posted to an SNS topic and notification sent to a sample email in case the threshold of 100 requests per minute is exceeded.

The following test cases have been configured directly on the Lambda from AWS Console due to easiness:

* JWT is missing from the request;
* JWT is tampered;
* database is not present in JWT;
* database 'movies' is queried;
* nonexistent database is queried.

# Usage

Assuming credentials are stored in `~/.aws/credentials` for a user with required privileges and an account is configured to connect to Serverless, a simple:

`sls deploy`

will load the stack to CloudFormation and expose the Lambda on AWS.
