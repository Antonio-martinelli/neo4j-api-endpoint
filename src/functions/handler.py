from neo4j import GraphDatabase, basic_auth
import json
import os
import jwt
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getEntryCount(event, context):
    """Function taking in input a JWT including a database's name
    used to connect to an instance and execute the count of the present nodes.
    """

    NEO4J_URI = os.environ['NEO4J_URI']
    NEO4J_USER = os.environ['NEO4J_USER']
    NEO4J_PASSWORD = os.environ['NEO4J_PASSWORD']
    JWT_SECRET = os.environ['JWT_SECRET']
    cypher_query = 'MATCH (n) RETURN COUNT(n) AS num'

    #Checking if JWT is present in the request
    try:
        encoded_jwt = event["headers"]["JWT"]
    except:
        logger.error('JWT is not specified.')
        return {
            "statusCode": 412,
            "headers": {
                "Content-Type": "application/json",
                "JWT": "missing"
            },
            "body": json.dumps({"message" : "JWT is not specified."})
        }
    
    #Checking if JWT is encrypted with proper JWT_SECRET
    try:
        jwt_decoded = jwt.decode(encoded_jwt, JWT_SECRET, algorithms=['HS256'])
    except:
        logger.error('JWT is tampered.')
        return {
            "statusCode": 401,
            "headers": {
                "Content-Type": "application/json",
                "JWT": json.dumps({"message" :encoded_jwt})
            },
            "body": json.dumps({"message" "JWT is tampered."})
        }

    #Checking if database to connect to is specified
    try:
        request_parameter = jwt_decoded['database']
    except:
        logger.error('Database to query is not specified.')
        return {
            "statusCode": 412,
            "headers": {
                "Content-Type": "application/json",
                "JWT": encoded_jwt
            },
            "body": json.dumps({"message" : "Database to query is not specified."})
        }

    #Checking if database is reachable
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
    except:
        logger.critical('The database is unreachable at the moment.')
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "JWT": encoded_jwt
            },
            "body": json.dumps({"message" : "The database is unreachable at the moment."})
        }

    #Running the query against the specified database and extracting the result
    try:
        with driver.session(database=request_parameter) as session:
            query_result = session.run(cypher_query)
            result = [record["num"] for record in query_result]
            result = str(result[0])
        driver.close()
    except:
        logger.error('The requested database does not exists.')
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
                "JWT": encoded_jwt
            },
            "body": json.dumps({"message" : "The requested database does not exists."})
        }

    #Returning the result
    logger.info('Query executed with result: ' + result)
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "JWT": encoded_jwt
            },
        "body": json.dumps({"message" : result})
    }
