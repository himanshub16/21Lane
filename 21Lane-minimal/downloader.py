from ftpclient import FTPClient
import ftplib  
import threading, os, time
from queue import Queue
from PyQt5.QtGui import QIcon, QPixmap

configFile = 'ftp-client.conf'

class Node:
	def __init__(self, hostname='locahost', port=2121, filesize=0, filename=None, destpath='', pathname=None, pbarsignal=None):
		if (not filename or not pathname):
			return None
		self.hostname = hostname
		self.port = port
		self.filesize = filesize 
		self.filename = filename 
		self.pathname = pathname 
		self.tries = 0
		self.destpath = destpath
		self.pbarsignal = pbarsignal


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
			self.downloadPath = os.path.join(os.path.expanduser('~'), 'Downloads')

	def downloader(self):
		completion = False

		# Thread to monitor download stats
		# ... commented as it caused lags.
		# changed completion label with progress bar
		# will try to implement in future versions
		def stats_monitor(state, filename, total_size, pbarsignal, targetFile):
			try:
				# guiwidget['state'] = 'running'
				# print("gui widget state running")
				print(targetFile)
				while state =='running':
					try:
						size = os.path.getsize(targetFile)
						completionPercent = ((100 * size) / float(total_size)) 
						pbarsignal.signal.emit(completionPercent)
						time.sleep(1)
					except FileNotFoundError as e:
						time.sleep(0.5)
						pass
					except ZeroDivisionError as e:
						pbarsignal.signal.emit(100)
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

			filename = node.filename
			pathname = node.pathname
			destpath = node.destpath
			# guiwidget = node.guiwidget
			state = 'somestate'

			if destpath.startswith('/'):
				destpath = destpath[1:]
			downloadPath = self.downloadPath
			if (destpath != ''):
				downloadPath = os.path.join(downloadPath, destpath)
				try:
					os.makedirs(downloadPath)
				except Exception as e:
					pass

			targetFile = os.path.join(downloadPath, filename)
			dummy = targetFile
			basename = os.path.splitext(targetFile)[0]
			extension = os.path.splitext(targetFile)[1]
			counter = 0
			while (os.path.exists(dummy)):
				dummy = basename+'_'+str(counter)+extension
				counter+=1
			if (counter != 0):
				targetFile = dummy


			try:
				completion = False
				total_size = node.filesize
				# guiwidget['statusicon'].setToolTip("In Queue")

				client = FTPClient(node.hostname, node.port)
				state = "running"
				th = threading.Thread(target=stats_monitor, args=(state, targetFile, total_size, node.pbarsignal, targetFile,))
				th.setDaemon(False)
				th.start()
				node.tries += 1
				# node.guiwidget['label'].setText("Downloading")
				# guiwidget['statusicon'].setPixmap(QPixmap('icons/running.svg'))
				# guiwidget['statusicon'].setToolTip('Downloading')
			except RuntimeError as e:
				continue

			try:
				if (node.tries < 4 and client.downloadFile(pathname=node.pathname, filename=node.filename, targetFile=targetFile)):
					# guiwidget['label'].setText("Completed")
					# guiwidget['statusicon'].setPixmap(QPixmap('icons/complete.svg'))
					# guiwidget['statusicon'].setToolTip('Completed')
					# guiwidget['pbar'].setValue(100)
					# guiwidget['state'] = 'completed'
					state = 'completed'
					node.pbarsignal.signal.emit(100)
					
				else:
					if (node.tries == 4):
						# guiwidget['label'].setText("Failed")
						# guiwidget['statusicon'].setPixmap(QPixmap('icons/failed.svg'))
						# guiwidget['statusicon'].setToolTip('Failed')
						# guiwidget['state'] = 'failed'
						state = 'failed'
						node.pbarsignal.signal.emit(-1)
					else:
						self.downloadQueue.put(node)
						# guiwidget['label'].setText("Waiting")
						# guiwidget['statusicon'].setPixmap(QPixmap('icons/wait.svg'))
						# guiwidget['statusicon'].setToolTip('Waiting')
						# node.guiwidget['state'] = 'waiting'
						state = 'waiting'
						node.pbarsignal.signal.emit(50)
				self.downloadQueue.task_done()
				completion = True

			except RuntimeError as e:
				pass

			except Exception as e:
				# node.guiwidget['statusicon'].setPixmap(QPixmap('icons/failed.svg'))
				# node.guiwidget['statusicon'].setToolTip("Network Error")
				# node.guiwidget['label'].setText("Network error. Retry")
				node.pbarsignal.emit(-10)
				raise e
				pass

	def addEntry(self, pathname, filesize, filename, pbarsignal, destpath='', hostname='localhost', port=2121):
		node = Node(hostname=hostname, port=port, pathname=pathname, filesize=filesize, filename=filename, pbarsignal=pbarsignal, destpath=destpath)
		if not Node:
			# node.guiwidget['state'] = 'failed'
			return False
		self.downloadQueue.put(node)