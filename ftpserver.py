#!/usr/bin/python
# source : https://pythonhosted.org/pyftpdlib/tutorial.html#building-a-base-ftp-server

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

import sys, os, json

STATS_FILE = "stats.json"
stats = {"connected":0, "files_transferred":0, "bytes_transferred":0, "failed_transfers":0, "bytes_transferred_str":"0"}

def getSize(filepath):
	try:
		return os.path.getsize(filepath)
	except OSError:
		return 0


class CustomHandler(FTPHandler):
	def on_connect(self):
		stats["connected"] += 1
		with open(STATS_FILE, "w") as f:
			f.write(json.dumps(stats))

	def on_disconnect(self):
		stats["connected"] -= 1
		with open(STATS_FILE, "w") as f:
			f.write(json.dumps(stats))
	
	def on_file_sent(self, file):
		stats["files_transferred"] += 1
		stats["bytes_transferred"] += getSize(file)
		with open(STATS_FILE, "w") as f:
			f.write(json.dumps(stats))

	def on_incomplete_file_sent(self, file):
		stats["failed_transfers"] += 1
		with open(STATS_FILE, "w") as f:
			f.write(json.dumps(stats))

def main(port, sharedLocation):
	authorizer = DummyAuthorizer()
	authorizer.add_anonymous(sharedLocation)

	handler = CustomHandler
	handler.authorizer = authorizer

	handler.banner = "21Lane sharing is ready"
	address = ("0.0.0.0", port)
	server = FTPServer(address, handler)

	server.max_cons = 256
	server.max_cons_per_ip = 5

	server.serve_forever()

if __name__ == "__main__":
	if (len(sys.argv) < 3):
		print("Insufficient arguments.")
		sys.exit()

	port = int(sys.argv[1])
	sharedLocation = sys.argv[2]
	main(port, sharedLocation)

