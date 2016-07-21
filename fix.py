import os

for root, dirs, files in os.walk('.'):
	for dir in dirs:
		os.chmod(os.path.abspath(dir), 775)

