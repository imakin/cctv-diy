import http.server
from multiprocessing import Process
def serve():
    http.server.test()

p = Process(target=serve)
p.start()
