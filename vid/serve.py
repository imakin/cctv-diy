import http.server
import socketserver
from multiprocessing import Process

import os
import sys
BASE_DIR = os.path.dirname( os.path.realpath(sys.argv[0]) )

os.chdir(BASE_DIR)
def serve():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

p = Process(target=serve, daemon=True)
p.start()
