import pydcop
import logging
import os
import util

class _DictionaryWrapper(object):
  """Wrapper around a public and private dictionary.

  Attribute-like access provided over the keys of the dictionaries, with
  the contents in the public dictionary winning in case of conflict.

  The public dictionary can be accessed using public(), so methods that want
  to export it can.

  Note that mutations are not allowed through attributes"""
  def __init__(self, public_dict, private_dict = {}):
    self.__dict__["_public"] = public_dict
    self.__dict__["_private"] = private_dict

  def __str__(self):
    ret = ""
    for (k, v) in self._public.items():
      ret += "%s: %s\n" % (k, v)
    for (k, v) in self._private.items():
      ret += "(%s: %s)\n" % (k, v)
    return ret

  def public(self):
    return self._public

  def __getattr__(self, name):
    if self._public.has_key(name):
      return self._public.get(name)
    elif self._private.has_key(name):
      return self._private.get(name)
    else:
      return object.__getattribute__(self, name)

  def __setattr__(self, name, value):
    if self.__dict__.has_key(name):
      self.__dict__[name] = value
    else:
      raise KeyError("Attribute mutation for dictionaries not supported")

class Amarok:
  def __init__(self):
    self._app = pydcop.anyAppCalled("amarok")
    self._errors = []
    if not self._app:
      self._AddError("No 'amarok' application registered with DCOP")
      return
    self._player = self._app.player
    self._playlist = self._app.playlist
    if not self._player:
      self._AddError("No 'player' object in the 'amarok' app")

  def _AddError(self, error):
    self._errors.append(error)
    logging.error(error)

  def Next(self):
    if len(self._errors) > 0: return False
    self._player.next()
    return True

  def Prev(self):
    if len(self._errors) > 0: return False
    self._player.prev()
    return True

  def JumpTo(self, trackid):
    self._playlist.playByIndex(trackid)

  def PlayPause(self):
    if len(self._errors) > 0: return False
    self._player.playPause()
    return True

  def CurrentTrack(self):
    if len(self._errors) > 0: return {}
    public = {}
    public['title'] = self._player.title()
    public['album'] = self._player.album()
    public['artist'] = self._player.artist()

    totaltime = self._player.trackTotalTime()
    currtime = self._player.trackCurrentTime()
    private = {}
    private['total_time'] = totaltime
    private['time_left'] = totaltime - currtime
    return _DictionaryWrapper(public, private)

  def IsPlaying(self):
    return self._player.isPlaying()

  def MatchingTracks(self, query, max_results=7):
    # TODO: We match 'query' as a full substring instead of considering it
    # as an AND of unigrams
    if not query or not len(query): return []
    candidates = self._playlist.filenames()
    results = []
    index = 0
    for c in candidates:
      c = os.path.splitext(c)[0]
      if c.lower().find(query) >= 0:
        results.append((index, c))
        if len(results) >= max_results:
          break
      index = index + 1
    return results

