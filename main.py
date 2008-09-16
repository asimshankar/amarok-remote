#!/usr/bin/env python

import getopt
import logging
import os
import sys

import BaseHTTPServer

import handler

program_name = ""

class BaseHTTPRequestHandlerRequest(handler.RequestInterface):
  def __init__(self, req):
    self._request = req;

  def Path(self):
    return self._request.path

  def ClientAddress(self):
    addr = self._request.client_address
    return "%s:%d" % (addr[0], addr[1])

  def Respond(self, code = 200, headers = {}, txt = ''):
    self._request.send_response(code)
    headers['Content-Length'] = len(txt)
    for (k, v) in headers.items():
      self._request.send_header(k, v)
    self._request.end_headers()
    self._request.wfile.write(txt)


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def do_GET(self):
    r = BaseHTTPRequestHandlerRequest(self)
    h = handler.Handler(r)
    h.Get()

  def log_error(self, *args):
    """Overrides base class implementation to log to the logging module instead
    of to sys.stderr"""
    if len(args):
      logging.error(args[0], *args[1:])
    else:
      logging.error(*args)

  def log_message(self, format, *args):
    """Overrides base class implementation to log to the logging module instead
    of to sys.stderr"""
    logging.debug(format % args)


def Usage():
  global program_name
  print """
Usage: %s [options]
Where [options] include:
  -h, --help                This message
  -pPORT, --port=PORT       Make the HTTP server listen on localhost:PORT
  -lLOGFILE, --log=LOGFILE  Write logs to LOGFILE
                            If this flag is not specified or LOGFILE is - then
                            logs are written to STDERR
  --minloglevel=LEVEL       Set the minimum level for messages to make it to
                            the log. Both numbers and names are fine. Default
                            is INFO. To add verbosity, set it to DEBUG
""" % (program_name)

def SetupLogging(logfile, level):
  #logging.basicConfig(format="[%(levelname)-8s %(asctime)s %(filename)s:"
                             #"%(lineno)s] %(message)s ",
                      #datefmt="%Y%m%d %H%M%S",
                      #level=logging.DEBUG)
  handler = None
  if logfile == "-":
    handler = logging.StreamHandler()
  else:
    handler = logging.FileHandler(logfile, "a")
  handler.setLevel(level)
  formatter = logging.Formatter(fmt="[%(levelname)-8s %(asctime)s %(filename)s:"
                                "%(lineno)s] %(message)s",
                                datefmt="%Y%m%d %H%M%S")
  handler.setFormatter(formatter)
  logger = logging.getLogger()
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)


def main():
  global program_name
  program_name = sys.argv[0]

  try:
    opts, args = getopt.getopt(sys.argv[1:],
                               "hp:l:",
                               [ "help",
                                 "port=",
                                 "log=",
                                 "minloglevel=",
                               ])
  except getopt.GetoptError, e:
    logging.error(str(e))
    print "Bad commandline arguments: " + str(e)
    Usage()
    sys.exit(2)

  port = 8080
  logfile = "-"
  logging_level = logging.getLevelName("INFO")
  bad_minloglevel = None
  for o,a in opts:
    if o in ("-h", "--help"):
      Usage()
      sys.exit()
    elif o in ("-p", "--port"):
      port = int(a)
    elif o in ("-l", "--log"):
      logfile = a
    elif o in ("--minloglevel"):
      if str(a).isdigit():
        logging_level = a
      elif str(logging.getLevelName(a)).isdigit():
        logging_level = logging.getLevelName(a)
      else:
        bad_minloglevel = a
    else:
      assert False, "Unhandled argument"

  SetupLogging(logfile, logging_level)
  # Log this only after setting up logging.
  if bad_minloglevel:
    logging.error("Bad --minloglevel (%s), using default (%s)" %
                  (bad_minloglevel, logging.getLevelName(logging_level)))

  try:
    http = BaseHTTPServer.HTTPServer(('', port), RequestHandler)
    logging.info("Started HTTPServer. PID: %d. Port %d" % (os.getpid(), port))
    http.serve_forever()
  except KeyboardInterrupt:
    logging.error("^C received. Shutting down")
    http.socket.close()

if __name__ == "__main__":
  main()
