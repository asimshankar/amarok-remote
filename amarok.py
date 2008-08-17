import pydcop
import logging
import util

class TrackInfo:
  def __init__(self, dict):
    for k in dict:
      if not self.__dict__.has_key(k):
        self.__dict__[k] = dict.get(k)
      else:
        logging.warning("TrackInfo already has a member: " + str(k))

  def __str__(self):
    ret = ""
    for k in self.__dict__:
      if not k.startswith("_"):
        ret += "%s: %s\n" % (k, self.__dict__.get(k))
    return ret

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
    dict = {}
    dict['title'] = self._player.title()
    dict['album'] = self._player.album()
    dict['artist'] = self._player.artist()
    totaltime = self._player.trackTotalTime()
    dict['total_time'] = totaltime
    dict['time_left'] = totaltime - self._player.trackCurrentTime()
    return TrackInfo(dict)

  def IsPlaying(self):
    return self._player.isPlaying()

  def MatchingTracks(self, query, max_results=5):
    # TODO: We match 'query' as a full substring instead of considering it
    # as an AND of unigrams
    if len(query) == 0: return []
    candidates = self._playlist.filenames()
    results = []
    index = 0
    for c in candidates:
      c = util.FileWithoutExtension(c) 
      if c.lower().find(query) >= 0:
        results.append((index, c))
        if len(results) > max_results:
          break
      index = index + 1
    return results

