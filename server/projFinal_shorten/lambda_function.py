import json
import os
import random
import string
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
    print(event)
    try:
        print("**STARTING**")
        print("**lambda: projFinal_shorten**")

        #
        # setup AWS based on config file:
        #
        config_file = 'config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        #
        # configure for RDS access
        #
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        #
        # open connection to the database:
        #
        print("**Opening connection**")

        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        #
        # check if request body is valid
        #
        print("**Accessing request body**")

        if "body" not in event:
            raise Exception("event has no body")
          
        body = json.loads(event["body"]) # parse the json

        if "longurl" not in body:
            raise Exception("event has a body but no longurl")
        longurl = body["longurl"]

        shorturlpath = None
        sql = "SELECT COUNT(*) AS count FROM urls WHERE shorturl = %s;"
        
        if "shorturlpath" not in body:
            print("event has a body but no shorturlpath")
        else:
            shorturlpath = body["shorturlpath"]
            if len(shorturlpath) > 16:
                raise Exception("shorturlpath too long")
            row = datatier.retrieve_one_row(dbConn, sql, [shorturlpath])
            if row[0] != 0:
                raise Exception("shorturl already used")

        #
        # generate short URL path if it is not provided
        #
        while shorturlpath is None:
            shorturlpath = "".join(random.choices(string.ascii_lowercase +
                                 string.digits, k=7))
            row = datatier.retrieve_one_row(dbConn, sql, [shorturlpath])
            if row[0] != 0:
                shorturlpath = None

        print("longurl:", longurl)
        print("shorturlpath:", shorturlpath)
        
        sql = "INSERT INTO urls(shorturl, longurl) VALUES(%s, %s);"
        datatier.perform_action(dbConn, sql, [shorturlpath, longurl])

        return {
            "statusCode": 200,
            "body": json.dumps({
                "longurl": longurl,
                "shorturlpath": shorturlpath
            })
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
          'statusCode': 400,
          'body': json.dumps(str(err))
        }
