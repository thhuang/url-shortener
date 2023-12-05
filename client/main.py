import requests
import json 

import pathlib
import logging
import sys

from configparser import ConfigParser


###################################################################
#
# prompt
#
def prompt():
    """
    Prompts the user and returns the command number

    Parameters
    ----------
    None

    Returns
    -------
    Command number entered by user (0, 1, 2, ...)
    """
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => generate a shortened URL")
    print("   2 => generate a URL with customized path")
    print("   3 => stats")

    cmd = int(input())
    return cmd


def shorten(baseurl):
    """
    Generate a shortened URL
    """

    print("Enter long URL>")
    longurl = input()

    try:
        data = {
            "longurl": longurl
        }

        api = '/shorten'
        url = baseurl + api

        res = requests.post(url, json=data)

        if res.status_code != 200:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if 400 <= res.status_code < 500:
                body = res.json()
                print("Error message:", body["message"])
            return

        body = res.json()

        shorturlpath = body["shorturlpath"]

        print("Shortened URL:", "{}/{}".format(baseurl, shorturlpath)) 

    except Exception as e:
        logging.error("shorten() failed:")
        logging.error("url: " + baseurl)
        logging.error(e)
        return


def customized(baseurl):
    """
    Generate a URL with customized path
    """

    print("Enter long URL>")
    longurl = input()

    print("Enter customized path>")
    shorturlpath = input()

    try:
        data = {
            "longurl": longurl,
            "shorturlpath": shorturlpath
        }

        api = '/shorten'
        url = baseurl + api

        res = requests.post(url, json=data)

        if res.status_code != 200:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if 400 <= res.status_code < 500:
                body = res.json()
                print("Error message:", body["message"])
            return

        body = res.json()

        shorturlpath = body["shorturlpath"]

        print("Shortened URL:", "{}/{}".format(baseurl, shorturlpath)) 

    except Exception as e:
        logging.error("customized() failed:")
        logging.error("url: " + baseurl)
        logging.error(e)
        return


def stats(baseurl):
    """
    Get the statistics of the usage of the shortened URL
    """

    print("Enter shortened URL path>")
    shorturlpath = input()

    try:
        api = '/stats'
        url = baseurl + api + '/' + shorturlpath

        res = requests.get(url)

        if res.status_code != 200:
            print("Failed with status code:", res.status_code)
            print("url: " + url)
            if 400 <= res.status_code < 500:
                body = res.json()
                print("Error message:", body["message"])
            return

        body_str = json.dumps(res.json(), indent=2)
        print(body_str)

    except Exception as e:
        logging.error("stats() failed:")
        logging.error("url: " + baseurl)
        logging.error(e)
        return


#########################################################################
# main
#
print('** Welcome to URL Shortener **')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'urlshortener-client-config.ini'

print("What config file to use for this session?")
print("Press ENTER to use default (urlshortener-client-config.ini),")
print("otherwise enter name of config file>")
s = input()

if s == "":  # use default
    pass  # already set
else:
    config_file = s

#
# does config file exist?
#
if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

#
# setup base URL to web service:
#
configur = ConfigParser()
configur.read(config_file)
baseurl = configur.get('client', 'webservice')

#
# main processing loop:
#
cmd = prompt()

while cmd != 0:
    #
    if cmd == 1:
        shorten(baseurl)
    elif cmd == 2:
        customized(baseurl)
    elif cmd == 3:
        stats(baseurl)
    else:
        print("** Unknown command, try again...")
    #
    cmd = prompt()

#
# done
#
print()
print('** done **')
