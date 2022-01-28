"""
Used for testing the TCPClient class.
"""

from libtcp import *

if __name__ == '__main__':
    client = TCPClient(remote_host='127.0.0.1', remote_port=65432)
    client.process_loop()
