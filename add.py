import os
f = open('modified', 'r')
lines = f.read()

for line in lines:
	os.system('git add '+line)
	print(line + ' added')
