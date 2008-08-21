import logging
import os
import simplejson

from BaseHTTPServer import BaseHTTPRequestHandler
from mako.template import Template
from mako.lookup import TemplateLookup

import amarok as Amarok
import util

class RequestHandler(BaseHTTPRequestHandler):
  def do_GET(self):
    (self.path, self.params) = util.ParseRequestPath(self.path)

    if self.path == "apple-touch-icon.png" or \
       self.path == "apple-touch-icon-precomposed.png":
      # Icon for iPhone webclip
      # See https://developer.apple.com/webapps/docs_iphone/documentation/AppleApplications/Reference/SafariWebContent/OptimizingforSafarioniPhone/chapter_3_section_4.html
      self.path = "static/apple-touch-icon.png"

    (topdir, suffix) = util.SplitPath(self.path)
    if topdir == "static":
      self._Static(suffix)
    elif topdir == "ajax":
      self._RunAjax(suffix)
    elif topdir == "":
      self._Render(suffix)
    else:
      self._NotFound()

  def _RunAjax(self, cmd):
    output = None
    amarok = Amarok.Amarok()
    error = False
    if cmd == "search":
      query = self.params.get("q")
      output = []
      if query:
        for r in amarok.MatchingTracks(query):
          output.append({ 'id' : r[0], 'name': r[1] })
    elif cmd == "status":
      pass
    elif cmd == "jumpto":
      track = self.params.get("t")
      if not track:
        logging.error("No track specified to jumpto request")
        error = True
      else:
        try:
          track = int(track)
          amarok.JumpTo(track)
        except ValueError:
          logging.error("Invalid jumpto request: track = %s" % track)
          error = True
    elif cmd == "playpause":
      amarok.PlayPause()
    elif cmd == "next":
      amarok.Next()
    elif cmd == "prev":
      amarok.Prev()
    else:
      logging.error("Unrecognized ajax command: %s in request %s" % (cmd,
                                                                     self.path))
      error = True

    if error:
      self._NotFound()
      return

    if output is None:
      output = {}
      output['track'] = amarok.CurrentTrack().public()
      output['playing'] = amarok.IsPlaying()

    # Using separators for compact JSON representation
    out_text = simplejson.dumps(output, separators=(',', ':'))
    self.send_response(200)
    self.send_header('Content-Type', 'text/html')
    self.send_header('Content-Length', len(out_text))
    self.end_headers()
    self.wfile.write(out_text)

  def _Render(self, page):
    lookup = TemplateLookup(directories=["templates"],
                            module_directory="tmp/mako")
    template = None
    args = {}
    amarok = Amarok.Amarok()
    if page == "" or page == "/home":
      template = lookup.get_template("home.html")
      args['track'] = amarok.CurrentTrack()
      args['amarok'] = amarok
    
    if not template:
      self._NotFound()
    else:
      output = template.render(**args)
      self.send_response(200)
      self.send_header('Content-Type', 'text/html')
      self.send_header('Content-Length', len(output))
      self.end_headers()
      self.wfile.write(output)

  def _Static(self, path):
    path = os.path.join("static", path)
    data = ""
    try:
      fd = open(path)
      data = fd.read()
    except (OSError, IOError), e:
      logging.error("Bad static request (%s) from %s:%d (Exception %s)" %
                    (path,
                     self.client_address[0],
                     self.client_address[1],
                     e))
      self.log_request()
      self._NotFound()
      return

    content_type = ''
    extension = os.path.splitext(path)[1]
    if extension == ".png":
      content_type = "images/jpeg"
    elif extension == ".js":
      content_type = "text/javascript"
    elif extension == ".css":
      content_type = "text/css"
    else:
      content_type = "images/jpeg"

    self.send_response(200)
    self.send_header('Content-Type', content_type)
    self.send_header('Content-Length', len(data))
    self.end_headers()
    self.wfile.write(data)

  def _RedirectHome(self):
    self.send_response(301)
    self.send_header('Location', '/')
    self.end_headers()

  def _NotFound(self):
    message = "File not found"
    self.send_response(404)
    self.send_header('Content-Type', 'text/html')
    self.send_header('Content-Length', len(message))
    self.end_headers()
    self.wfile.write(message)
