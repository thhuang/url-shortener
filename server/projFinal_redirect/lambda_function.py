import json
import os
import datatier
import requests
from datetime import datetime, timezone
from user_agents import parse
from configparser import ConfigParser

def get_location(ip_address):
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    print(response)
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: projFinal_redirect**")

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
        # shorturlpath from event: could be a parameter
        # or could be part of URL path ("pathParameters"):
        #
        print("**Accessing event/pathParameters**")

        if "shorturlpath" in event:
            shorturlpath = event["shorturlpath"]
        elif "pathParameters" in event:
            if "shorturlpath" in event["pathParameters"]:
                shorturlpath = event["pathParameters"]["shorturlpath"]
            else:
                raise Exception("requires shorturlpath parameter in pathParameters")
        else:
            raise Exception("requires shorturlpath parameter in event")
            
        print("shorturlpath:", shorturlpath)

        #
        # open connection to the database:
        #
        print("**Opening connection**")

        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        sql = "SELECT urlid, longurl FROM urls WHERE shorturl = %s;"
        row = datatier.retrieve_one_row(dbConn, sql, [shorturlpath])
        if len(row) == 0:
            return {
                "statusCode": 404,
                "body": json.dumps("not found")
            }

        urlid = int(row[0])
        longurl = row[1]
        print(urlid, longurl)
        
        try:
            print(event)
            print(event['headers'])
            
            location_data = get_location(event['headers']['X-Forwarded-For'])
            ip = location_data['ip']
            city = location_data['city']
            region = location_data['region']
            country = location_data['country']
            print(ip, city, region, country)
            
            useragent = parse(event['headers']['User-Agent'])
            browser = useragent.browser.family
            device_os = useragent.os.family
            device = useragent.device.family
            print(browser, device_os, device)
            
            now = datetime.now(timezone.utc)
            
            sql = "INSERT INTO history(urlid, created, ip, city, region, country, browser, os, device) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            datatier.perform_action(dbConn, sql, [urlid, now, ip, city, region, country, browser, device_os, device])

        except Exception as err:
            print("cannot get stats")
            print(str(err))

        return {
            "statusCode": 302,
            "headers": {
                "Location": longurl
            }
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
          'statusCode': 400,
          'body': json.dumps(str(err))
        }
