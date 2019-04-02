#!/usr/bin/python3.6

import sys
import csv
import logging
from logging.handlers import RotatingFileHandler

try:
	import requests
except ImportError:
	print('ImportError: requests module')
	sys.exit(1)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('logs.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)
logging.getLogger("requests").setLevel(logging.WARNING)

def main():
	with open('mapping.csv') as mapping:
		rows = csv.reader(mapping)
		for row in rows:
			url = row[0]
			version = row[1]
			headers = getResponseHeader(url, version)
	
def getResponseHeader(url, version):
	payload = {"service":"WMS", "request":"GetCapabilities","version":version}
	r = requests.head(url, params=payload)
	
	if r.status_code == 200:
		logger.debug(url + ' -- ' + str(r.status_code))
		return r.headers
	else:
		logger.error(url + ' -- ' + str(r.status_code))
		return None

if __name__ == '__main__':
	main()