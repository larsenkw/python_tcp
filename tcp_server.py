"""
Used for runninging the TCPServer class.
"""

from libtcp import *

if __name__ == '__main__':
    server = TCPServer()
    server.process_loop()
