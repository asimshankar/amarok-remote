import dcopext
import logging
import os
import util

def _UnicodeToAscii(string):
  """Converts a given string (ascii or unicode) into a unicode-escaped ASCII string"""
  return unicode(string).encode('utf-8')

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

class _SafeDCOPMeth:
  def __init__(self, dcop_method):
    self._dcop_method = dcop_method

  def __call__(self, *args):
    (ok, result) = self._dcop_method.__call__(*args)
    if not ok:
      raise RuntimeError(str(self) + ": " + str(ok) + " -- " + str(result))
    else:
      logging.debug(str(self) + ": " + str(ok) + " -- " + _UnicodeToAscii(result))
    return result

  def __str__(self):
    return "SafeDCOPMeth(" + str(self._dcop_method) + ")"


class _SafeDCOPObj:
  def __init__(self, dcop_object):
    self.__dict__['_dcop_object'] = dcop_object

  def __getattr__(self, name):
    obj = self.__dict__['_dcop_object']
    ret = _SafeDCOPMeth(obj.__getattr__(name))
    return ret

  def __str__(self):
    return "SafeDCOPObj(" + str(self._dcop_object) + ")"


class Amarok:
  def __init__(self):
    client = dcopext.DCOPClient()
    if not client.attach():
      logging.fatal("Unable to attach to the DCOP server")
    self._app = dcopext.DCOPApp("amarok", client)
    self._errors = []
    if not self._app:
      self._AddError("No 'amarok' application registered with DCOP")
      return
    self._player = _SafeDCOPObj(self._app.player)
    self._playlist = _SafeDCOPObj(self._app.playlist)
    self._cover_image_dir = os.path.dirname(self._player.coverImage())

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
    public['cover_image'] = os.path.basename(self._player.coverImage())

    totaltime = self._player.trackTotalTime()
    currtime = self._player.trackCurrentTime()
    private = {}
    private['total_time'] = totaltime
    private['time_left'] = totaltime - currtime
    return _DictionaryWrapper(public, private)

  def CoverImagePath(self, image):
    return os.path.join(self._cover_image_dir, image)

  def IsPlaying(self):
    return self._player.isPlaying()

  def Volume(self):
    return self._player.getVolume()

  def SetVolumeRelative(self, ticks):
    return self._player.setVolumeRelative(ticks)

  def MatchingTracks(self, query, max_results=7):
    # TODO: We match 'query' as a full substring instead of considering it
    # as an AND of unigrams
    if not query or not len(query): return []
    candidates = [unicode(x) for x in self._playlist.filenames()]
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

