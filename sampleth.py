import threading, time

class myThread(threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

	def run(self):
		print("Starting ", self.name)
		print_time(self.name, self.counter, 1)
		print ("thread ", self.threadID, " exits")


def print_time(threadName, ctr,  delay):
	count = 0
	while count < ctr:
		time.sleep(delay)
		count += 1
		print("%s %s " % (threadName, time.ctime(time.time())))

thread1 = myThread(1, "thread 1", 10)
thread2 = myThread(2, "thread 2", 20)

thread1.start()
thread2.start()
print ("main thread exits")
x = int(input())
print (x)
