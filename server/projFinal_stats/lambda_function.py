import json
import os
import datatier
from configparser import ConfigParser
from collections import defaultdict

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

        sql = '''
        SELECT h.created, h.ip, h.city, h.region, h.country, h.browser, h.os, h.device FROM urls u
        JOIN history h ON u.urlid = h.urlid
        WHERE u.shorturl = %s;
        '''
        rows = datatier.retrieve_all_rows(dbConn, sql, [shorturlpath])
        
        if len(rows) == 0:
            sql = "SELECT COUNT(*) FROM urls WHERE shorturl = %s;"
            row = datatier.retrieve_one_row(dbConn, sql, [shorturlpath])
            if row[0] == 0:
                return {
                    "statusCode": 404,
                    "body": json.dumps("not found")
                }

        hour_stats = {t: 0 for t in range(24)}
        city_stats = defaultdict(int)
        ip_stats = defaultdict(int)
        region_stats = defaultdict(int)
        country_stats = defaultdict(int)
        browser_stats = defaultdict(int)
        device_os_stats = defaultdict(int)
        device_stats = defaultdict(int)
        for created, ip, city, region, country, browser, device_os, device in rows:
            hour_stats[created.hour] += 1
            city_stats[city] += 1
            ip_stats[ip] += 1
            region_stats[region] += 1
            country_stats[country] += 1
            browser_stats[browser] += 1
            device_os_stats[device_os] += 1
            device_stats[device] += 1
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "usage": len(rows),
                "hourStats": hour_stats,
                "cityStats": city_stats,
                "ipStats": ip_stats,
                "regionStats": region_stats,
                "countryStats": country_stats,
                "browserStats": browser_stats,
                "osStats": device_os_stats,
                "deviceStats": device_stats
            })
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
          'statusCode': 400,
          'body': json.dumps(str(err))
        }
