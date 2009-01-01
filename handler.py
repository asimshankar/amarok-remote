import logging
import os
import simplejson

from mako.template import Template
from mako.lookup import TemplateLookup

import amarok as Amarok
import util

class RequestInterface:
  """Generic interface for Request object used by the Handler class

  This interface is more to document what needs to be implemented"""
  def Respond(self, code, headers, txt):
    raise Exception("Respond() not implemented")

  def Path(self):
    raise Exception("Path() not implemented")

  def ClientAddress(self):
    raise Exception("ClientAddress() not implemented")


class Handler:
  def __init__(self, request):
    self.request = request

  def Get(self):
    (self.path, self.params) = util.ParseRequestPath(self.request.Path())
    logging.debug(self.path)
    if self.path == "apple-touch-icon.png" or \
       self.path == "apple-touch-icon-precomposed.png" or \
       self.path == "favicon.ico":
      # Icon for iPhone webclip
      # See https://developer.apple.com/webapps/docs_iphone/documentation/AppleApplications/Reference/SafariWebContent/OptimizingforSafarioniPhone/chapter_3_section_4.html
      self.path = "static/apple-touch-icon.png"

    (topdir, suffix) = util.SplitPath(self.path)
    if topdir == "static":
      self._HandleLocalFile(self.path)
    elif topdir == "ajax":
      self._RunAjax(suffix)
    elif topdir == "covers":
      image_path = Amarok.Amarok().CoverImagePath(suffix)
      self._HandleLocalFile(path=image_path, content_type="images/jpeg")
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
    elif cmd == "changevolume":
      ticks = self.params.get("v")
      if ticks:
        try:
          ticks = int(ticks)
          amarok.SetVolumeRelative(ticks)
        except ValueError:
          logging.error("Invalid changevolume request: ticks = %s" % ticks)
          error = True
    else:
      logging.error("Unrecognized ajax command: %s in request %s" % (cmd,
                                                                     self.path))
      error = True

    if error:
      self._NotFound()
      return

    if output is None:
      output = {}
      track = amarok.CurrentTrack()
      output['track'] = track.public()
      output['playing'] = amarok.IsPlaying()
      output['volume'] = amarok.Volume()
      output['time_left'] = track.time_left

    # Using separators for compact JSON representation
    out_text = simplejson.dumps(output, separators=(',', ':'))
    headers = { 'Content-Type': 'text/plain' }
    self.request.Respond(code = 200, headers = headers, txt = out_text)

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
      headers = { 'Content-Type': 'text/html' }
      self.request.Respond(code = 200, headers = headers, txt = output)

  def _HandleLocalFile(self, path, content_type = ""):
    data = ""
    try:
      fd = open(path)
      data = fd.read()
    except (OSError, IOError), e:
      logging.error("Bad static request (%s) from %s (Exception %s)" %
                    (path, self.request.ClientAddress(), e))
      self._NotFound()
      return

    if not content_type:
      extension = os.path.splitext(path)[1]
      if extension == ".png":
        content_type = "images/jpeg"
      elif extension == ".js":
        content_type = "text/javascript"
      elif extension == ".css":
        content_type = "text/css"
      else:
        content_type = "images/jpeg"

    headers = { 'Content-Type': content_type }
    self.request.Respond(code = 200, headers = headers, txt = data)

  def _RedirectHome(self):
    headers = { 'Location': '/' }
    self.request.Respond(code = 301, headers = headers) 

  def _NotFound(self):
    message = "File not found"
    headers = { 'Content-Type': 'text/html' }
    self.request.Respond(code = 400, headers = headers, txt = message)
