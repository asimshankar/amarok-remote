import logging
import os

from BaseHTTPServer import BaseHTTPRequestHandler
from mako.template import Template

import amarok as Amarok

class RequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    self.path = self.path.lower()
    self.amarok = Amarok.Amarok()

    if self.path == "/apple-touch-icon.png" or \
       self.path == "/apple-touch-icon-precomposed.png":
      # Icon for iPhone webclip
      # See https://developer.apple.com/webapps/docs_iphone/documentation/AppleApplications/Reference/SafariWebContent/OptimizingforSafarioniPhone/chapter_3_section_4.html
      self.path = "static/apple-touch-icon.png"

    if self.path.find("static/") >= 0:
      self._Static()
    elif self.path == "/next":
      self._Next()
    elif self.path == "/prev":
      self._Prev()
    elif self.path == "/playpause":
      self._PlayPause()
    else:
      self._Main()

  def _Main(self):
    self.path = "/"
    home_template = Template(filename="templates/home.html")
    self.send_response(200)
    self.send_header('Content-Type', 'text/html')
    self.end_headers()

    self.wfile.write(home_template.render(track=self.amarok.CurrentTrack(),
                                          amarok=self.amarok))

  def _Static(self):
    if self.path.find("static/") < 0:
      logging.fatal("_Static() call for non-static request: " + self.path)
      return

    if self.path.startswith("/"):
      self.path = self.path[1:]
    data = ""

    try:
      fd = open(self.path)
      data = fd.read()
    except OSError, e:
      logging.error("Bad static request (%s) from %s:%d (Exception %s)" %
                    (self.path, 
                     self.client_address[0],
                     self.client_address[1],
                     e))
      self.log_request()

    self.send_response(200)
    self.send_header('Content-Type', 'images/jpeg')
    self.send_header('Content-Length', len(data))
    self.end_headers()
    self.wfile.write(data)

    
  def _Next(self):
    self.amarok.Next()
    self._RedirectHome()

  def _Prev(self):
    self.amarok.Prev()
    self._RedirectHome()

  def _PlayPause(self):
    self.amarok.PlayPause()
    self._RedirectHome()

  def _RedirectHome(self):
    self.send_response(301)
    self.send_header('Location', '/')
    self.end_headers()
