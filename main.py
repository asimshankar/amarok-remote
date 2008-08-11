#!/usr/bin/env python

import logging
import os

from BaseHTTPServer import HTTPServer

import server

def main():
  logging.basicConfig(format=("[%(levelname)-8s %(asctime)s %(filename)s:"
                              "%(lineno)s] %(message)s "),
                      level=logging.DEBUG)
  try:
    port = 8080
    http = HTTPServer(('', port), server.RequestHandler)
    logging.info("Started HTTPServer. PID: %d. Port %d" % (os.getpid(), port))
    http.serve_forever()
  except KeyboardInterrupt:
    logging.error("^C received. Shutting down")
    http.socket.close()

if __name__ == "__main__":
  main()
