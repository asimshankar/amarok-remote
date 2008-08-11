#!/usr/bin/env python

import getopt
import logging
import os
import sys

from BaseHTTPServer import HTTPServer

import server

program_name = ""
def usage():
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
    usage()
    sys.exit(2)

  port = 8080
  for o,a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-p", "--port"):
      port = int(a)
    else:
      assert False, "Unhandled argument"

  try:
    http = HTTPServer(('', port), server.RequestHandler)
    logging.info("Started HTTPServer. PID: %d. Port %d" % (os.getpid(), port))
    http.serve_forever()
  except KeyboardInterrupt:
    logging.error("^C received. Shutting down")
    http.socket.close()

if __name__ == "__main__":
  main()
