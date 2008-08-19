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
    elif topdir == "cmd":
      if self._RunCommand(suffix):
        self._RedirectHome()
      else:
        self._NotFound()
    elif topdir == "ajax":
      self._RunAjax(suffix)
    elif topdir == "":
      self._Render(suffix)
    else:
      self._NotFound()

  def _RunCommand(self, cmd):
    amarok = Amarok.Amarok()
    success = True
    if cmd == "next":
      amarok.Next()
    elif cmd == "prev":
      amarok.Prev()
    elif cmd == "playpause":
      amarok.PlayPause()
    elif cmd == "jumpto":
      track = self.params.get("t")
      if track is not None:
        try:
          track = int(track)
          amarok.JumpTo(track)
        except ValueError:
          logging.error("Invalid jumpto request: track = %s" % track)
    else:
      logging.error("Unrecognized command: %s in request %s" % (cmd, self.path))
      success = False
    return success

  def _RunAjax(self, cmd):
    outdict = {}
    amarok = Amarok.Amarok()
    if cmd == "search":
      output = self._Search()
      self.send_response(200)
      self.send_header('Content-Type', 'text/html')
      self.end_headers()
      self.wfile.write(output)
      return
    elif cmd == "status":
      outdict = amarok.CurrentTrack().public()
    elif cmd == "playpause":
      amarok.PlayPause()
      outdict['playing'] = amarok.IsPlaying()
    elif cmd == "next":
      amarok.Next()
      outdict = amarok.CurrentTrack().public()
    elif cmd == "prev":
      amarok.Prev()
      outdict = amarok.CurrentTrack().public()
    else:
      logging.error("Unrecognized ajax command: %s in request %s" % (cmd,
                                                                     self.path))
      self._NotFound()
      return
    # Using separators for compact JSON representation
    output = simplejson.dumps(outdict, separators=(',', ':'))
    self.send_response(200)
    self.send_header('Content-Type', 'text/html')
    self.send_header('Content-Length', len(output))
    self.end_headers()
    self.wfile.write(output)


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
    if extension == "png":
      content_type = "images/jpeg"
    elif extension == "js":
      content_type = "text/javascript"
    elif extension == "css":
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

  def _Search(self):
    amarok = Amarok.Amarok()
    output = ""
    query = self.params.get("q")
    if query:
      results = amarok.MatchingTracks(query)
      for r in results:
        output += "<a href=/cmd/jumpto?t=%d>%s</a>&nbsp;&nbsp;" % (r[0], r[1])
      if len(output) == 0:
        output = "No matching tracks"
    return output

  def _NotFound(self):
    message = "File not found"
    self.send_response(404)
    self.send_header('Content-Type', 'text/html')
    self.send_header('Content-Length', len(message))
    self.end_headers()
    self.wfile.write(message)
