#!/usr/bin/python3
#
# Original Author : Himanshu Shekhar < https://github.com/himanshub16 >
#
# program to find if any python packages do not exist on a system
# this ensures that the python script do not fail because of missing modules

# It checks for all the files/source codes for required packages and then check whether they are installed in the system.

# Ported to python 3
# Author: Ramiz Muharemovic
# https://github.com/muharemovic

try:
	import sys, os
	import __main__ as main
except ImportError:
	print ("The sys and os modules could not be loaded. Please check you python installation.")
	exit(1)

print ("Is this script in the required directory? (y/n) ")
x = input().lower()

if not (x == "y"):
	print ("Make sure the above condition is satisfied!")
	exit(1)

# this part scans for python files recursively
filelist = []
for root, dirname, filename in os.walk(os.getcwd()):
	for var in filename:
		if var.endswith('.py'):
			filelist.append(os.path.join(root, var))

#filelist.remove(main.__file__)

modulelist = list() # list of modules to be checked for
for file in filelist:
	f = open(file, 'r')
	if file.endswith(main.__file__):
		continue
	# print ('evaluating file: ', file)
	content = f.readlines()

	for line in content:
		var = line.strip()
		if var.startswith('import') or var.startswith('from'):
			try:
				var = var.replace(',','\n')
				var = var.split()
				if 'as' in var:
					var.remove(var[var.index('as')+1])
				if 'from' in var:
					var.remove(var[var.index('from')+3])
				if 'import' in var:
					var.remove('import')
				if 'as' in var:
					var.remove('as')
				if 'from' in var:
					var.remove('from')

				for modname in var:
					modulelist.append(modname)
			except Exception as e:
				pass
	f.close()


# the variable modulelist holds the names of modules imported somewhere

# removing duplicates from the list of modules obtained
modulelist = list(set(modulelist))
# print modulelist
print ('==========================================================')
print ("Got names of modules, checking each one of them")
choice = input("Do you want to download any modules that are unavailable (requires pip)? (y/n) ").lower()
print()
for modulename in modulelist:
	var = 'import ' + modulename
	try:
		exec (var)
		print(modulename)
	except ImportError:
		#print ('**"', var.replace('import',''), '" cannot be imported. **')
		if choice == 'y':
			os.system('pip install ' + var.replace('import',''))
	except Exception as e:
		pass
	else:
		#print (var.replace('import',''), 'imported successfully.')
		pass

print()
print ("Thanks for using! ")
exit(0)
