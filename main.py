#!/usr/bin/env python

import getopt
import logging
import os
import sys

from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler

import handler

program_name = ""

class BaseHTTPRequestHandlerRequest(handler.RequestInterface):
  def __init__(self, req):
    self._request = req;

  def Path(self):
    return self._request.path

  def Respond(self, code = 200, headers = {}, txt = ''):
    self._request.send_response(code)
    headers['Content-Length'] = len(txt)
    for (k, v) in headers.items():
      self._request.send_header(k, v)
    self._request.end_headers()
    self._request.wfile.write(txt)


class RequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    r = BaseHTTPRequestHandlerRequest(self)
    h = handler.Handler(r)
    h.Get()


def Usage():
  global program_name
  print """
Usage: %s [options]
Where [options] include:
  -h, --help            This message
  -pPORT, --port=PORT   Make the HTTP server listen on localhost:PORT
""" % (program_name)

def main():
  logging.basicConfig(format=("[%(levelname)-8s %(asctime)s %(filename)s:"
                              "%(lineno)s] %(message)s "),
                      level=logging.DEBUG)
  global program_name
  program_name = sys.argv[0]

  try:
    opts, args = getopt.getopt(sys.argv[1:],
                               "hp:",
                               [ "help",
                                 "port=",
                               ])
  except getopt.GetoptError, e:
    logging.error(str(e))
    print "Bad commandline arguments: " + str(e)
    Usage()
    sys.exit(2)

  port = 8080
  for o,a in opts:
    if o in ("-h", "--help"):
      Usage()
      sys.exit()
    elif o in ("-p", "--port"):
      port = int(a)
    else:
      assert False, "Unhandled argument"

  try:
    http = HTTPServer(('', port), RequestHandler)
    logging.info("Started HTTPServer. PID: %d. Port %d" % (os.getpid(), port))
    http.serve_forever()
  except KeyboardInterrupt:
    logging.error("^C received. Shutting down")
    http.socket.close()

if __name__ == "__main__":
  main()
