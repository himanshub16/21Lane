from ftpclient import FTPClient
import ftplib 
import threading, os, time
from queue import Queue
from PyQt5.QtGui import QIcon, QPixmap

configFile = 'ftp-client.conf'

class Node:
	def __init__(self, hostname='locahost', port=2121, filesize=0, filename=None, destpath='', pathname=None, guiwidget=None):
		if (not filename or not pathname):
			return None
		self.hostname = hostname
		self.port = port
		self.filesize = filesize 
		self.filename = filename 
		self.pathname = pathname 
		self.tries = 0
		self.destpath = destpath
		self.guiwidget = guiwidget


class Downloader:
	def __init__(self):
		self.downloadQueue = Queue(maxsize=0)
		self.maxWorkers = 2
		self.execute = True
		self.lock = threading.Lock()
		self.getDownloadPath()
		self.threadMonitor = threading.Thread(target=self.running_listener)
		self.threadMonitor.setDaemon(True)
		self.threadMonitor.start()

	def running_listener(self):
		while True:
			if self.execute == True and threading.active_count() == 2:
				for i in range(self.maxWorkers):
					worker = threading.Thread(target=self.downloader)
					worker.setDaemon(True)
					worker.start()

			time.sleep(1)
	
	def getDownloadPath(self):
		try:
			conf = open(configFile, 'r')
			self.downloadPath = conf.readline().strip()
			conf.close()
			if (len(self.downloadPath) == 0):
				raise IOError
		except IOError:
			self.downloadPath = os.path.join(os.path.expanduser('~'), 'Download')

	def downloader(self):
		completion = False

		# Thread to monitor download stats
		# ... commented as it caused lags.
		# changed completion label with progress bar
		# will try to implement in future versions
		def stats_monitor(filename, total_size, guiwidget, destpath):
			try:
				if destpath.startswith('/'):
					destpath = destpath[1:]
				downloadPath = self.downloadPath
				if (destpath != ''):
					downloadPath = os.path.join(downloadPath, destpath)
				destination = os.path.join(downloadPath, destpath)
				guiwidget['state'] = 'running'
				print("gui widget state running")
				print(destination, filename)
				while guiwidget['state'] =='running':
					try:
						size = os.path.getsize(os.path.join(destination, filename))
						completionPercent = ((100 * size) / float(total_size)) 
						# guiwidget['pbar'].setValue(completionPercent)
						guiwidget['pbar'](completionPercent)
						time.sleep(1)
					except FileNotFoundError as e:
						print("File not found")
						pass
					except Exception as e:
						raise e
			except RuntimeError as e:
				return
			
			except Exception as e:
				raise e

		while True and self.execute:
			self.lock.acquire()
			node = self.downloadQueue.get()
			self.lock.release()
			try:
				completion = False
				total_size = node.filesize
				guiwidget = node.guiwidget
				guiwidget['statusicon'].setToolTip("In Queue")

				client = FTPClient(node.hostname, node.port)
				filename = node.filename
				destpath = node.destpath
				th = threading.Thread(target=stats_monitor, args=(filename, total_size, guiwidget, destpath,))
				th.setDaemon(False)
				th.start()
				node.tries += 1
				# node.guiwidget['label'].setText("Downloading")
				node.guiwidget['statusicon'].setPixmap(QPixmap('icons/running.svg'))
				node.guiwidget['statusicon'].setToolTip('Downloading')
			except RuntimeError as e:
				continue

			try:
				if (node.tries < 4 and client.downloadFile(pathname=node.pathname, filename=node.filename, destpath=node.destpath)):
					# guiwidget['label'].setText("Completed")
					guiwidget['statusicon'].setPixmap(QPixmap('icons/complete.svg'))
					guiwidget['statusicon'].setToolTip('Completed')
					node.guiwidget['state'] = 'completed'
					
				else:
					if (node.tries == 4):
						# guiwidget['label'].setText("Failed")
						guiwidget['statusicon'].setPixmap(QPixmap('icons/failed.svg'))
						guiwidget['statusicon'].setToolTip('Failed')
						node.guiwidget['state'] = 'failed'
					else:
						self.downloadQueue.put(node)
						# guiwidget['label'].setText("Waiting")
						guiwidget['statusicon'].setPixmap(QPixmap('icons/wait.svg'))
						guiwidget['statusicon'].setToolTip('Waiting')
						node.guiwidget['state'] = 'waiting'
				self.downloadQueue.task_done()
				completion = True

			except RuntimeError as e:
				pass

			except Exception as e:
				node.guiwidget['statusicon'].setPixmap(QPixmap('icons/failed.svg'))
				node.guiwidget['statusicon'].setToolTip("Network Error")
				# node.guiwidget['label'].setText("Network error. Retry")
				raise e
				pass

	def addEntry(self, pathname, filesize, filename, guiwidget, destpath='', hostname='localhost', port=2121):
		node = Node(hostname=hostname, port=port, pathname=pathname, filesize=filesize, filename=filename, guiwidget=guiwidget, destpath=destpath)
		if not Node:
			node.guiwidget['state'] = 'failed'
			return False
		self.downloadQueue.put(node)