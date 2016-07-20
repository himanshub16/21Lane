import sqlite3 as lite
import sys, os

if __name__ == '__main__':
	sys.exit()

if 'connected_users.db' in os.listdir(os.getcwd()):
	os.remove('connected_users.db')
con = lite.connect('connected_users.db')
cur = con.cursor()

maintext = """
	CREATE TABLE Users (
		SESSION_ID TEXT PRIMARY KEY,
		IP_ADDRESS TEXT,
		SHARED_SIZE REAL,
		FILENAME TEXT
	)
	"""

cur.execute(maintext)
con.commit()
cur.close()
print("database created")