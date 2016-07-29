"""
This script finds the total size of an ftp directory by recursively opening directories
@author: Albert Wang (albertyw@mit.edu)
September 18, 2010
"""
from ftplib import FTP
import re
import sys
from optparse import OptionParser


"""
This script finds the total size of an ftp directory by recursively opening directories
@author: Albert Wang (albertyw@mit.edu)
September 18, 2010
"""
from ftplib import FTP
import re
import sys


class FtpSize():
    def __init__(self, server, port, login, password, directory):
        """
        Initialize variables
        """
        self.ftp = FTP()
        self.ftp.connect(server, port)
        self.ftp.login(login, password)
        self.ftp.set_pasv(True)
        if directory == None:
            directory = self.ftp.pwd()
        self.human_readable = True
        self.current_directory = directory
        self.size = 0
        self.directory_queue = [self.current_directory]
        self.node_name_index = 0

    def find_node_name_index(self, line):
        self.node_name_index = len(line) - len(self.first_line_node)

    def run(self):
        """
        Start the recursive calculation
        """
        while len(self.directory_queue) > 0:
            self.current_directory = self.directory_queue.pop(0)
            self.ftp.sendcmd('NOOP')
            self.calculate_size()
        self.ftp.close()
        if self.human_readable:
            return self.convert_bytes(self.size)
        else:
            return self.size

    def calculate_size(self):
        """ 
        List and parse a directory listing
        """
        try:
            self.ftp.cwd(self.current_directory)
        except:
            print("got an error for ", self.current_directory)   
        current_directory_listing = self.ftp.nlst()
        if len(current_directory_listing) == 0:
            return
        self.first_line_node = current_directory_listing[0]
        self.ftp.retrlines('LIST', self.parse_line)
        self.node_name_index = 0 

    def parse_line(self, line):
        """ 
        Parse the returned string of the LIST command
        Python's retrlines function already splits each line
        """
        node_info = line.split()
        if not re.match('[-drwx]*', node_info[0]):
            pass
        if self.node_name_index == 0:
            self.find_node_name_index(line)
        node_name = node_info[8]
        permissions = node_info[0]
        node_name = line[self.node_name_index-1:len(line)].strip()
        if permissions[0] == 'd':
            self.directory_queue.append(self.current_directory + '/' + node_name.strip())
        if node_name == '.' or node_name == '..':
            return
        self.size += int(node_info[4])

    def convert_bytes(self, bytes):
        """
        Helper function to convert bytes into readable form (1024 => 1K)
        """
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fT' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fG' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fM' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fK' % kilobytes
        else:
            size = '%.2fb' % bytes
        print(bytes, ' bytes')
        return size


def print_help():
    print ('python ftpsize.py server login password [directory]')

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-p", "--port", help="Port number",
        dest='port', default=21, type="int")
    parser.add_option("-u", "--user", help="User name",
        dest='login', default="anonymous")
    parser.add_option("-w", "--password", help="password",
        dest='password', default="")
    parser.add_option("-d", "--directory", help="Directory to analyze",
        dest='directory', default=None)

    args, opts = parser.parse_args()
   
    if len(opts) == 0:
        print("Enter URL / IP address")
        sys.exit()

    server = opts[0]
    ftp_size = FtpSize(server, args.port, args.login, args.password, args.directory)
    print('size is ',ftp_size.run())

# if __name__ == "__main__":
#     help_functions = ['help', '-h']
#     if len(sys.argv) != 4 and len(sys.argv) != 5:
#         print_help()
#         sys.exit(0)
#     if sys.argv[1] in help_functions:
#         print_help()
#         sys.exit(0)
#     server = sys.argv[1]
#     login = sys.argv[2]
#     password = "" 
#     if len(sys.argv) == 5:
#         directory = sys.argv[3]
#     else:
#         directory = None
#     ftp_size = FtpSize(server, port, login, password, directory)
#     print (ftp_size.run())
