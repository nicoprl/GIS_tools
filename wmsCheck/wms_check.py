#!/usr/bin/python3.6

import sys
import argparse
import csv
import logging
from logging.handlers import RotatingFileHandler

try:
    import requests
except ImportError:
    print('ImportError: requests module')
    sys.exit(1)

def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler('logs.log', 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('csv', metavar='csv file', help='path to csv file')
    args = parser.parse_args()
    
    with open(args.csv) as mapping:
        rows = csv.reader(mapping)
        for row in rows:
            service = row[0]
            url = row[1]
            version = row[2]
            headers = getResponseHeader(url, service, version, logger)
    
def getResponseHeader(url, service, version, logger):
    payload = {"service":service, "request":"GetCapabilities", "version":version}
    r = requests.head(url, params=payload)
    
    if r.status_code != 200:
        logger.error(url + ' -- ' + str(r.status_code))
        return r.headers
    else:
        logger.info(url + ' -- ' + str(r.status_code))
        return r.headers

if __name__ == '__main__':
    main()
