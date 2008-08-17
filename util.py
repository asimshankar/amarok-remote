import logging
import urllib

def FileExtension(filename):
  pos = filename.rfind('.')
  if pos == -1: return ''
  return filename[pos+1:]

def FileWithoutExtension(filename):
  pos = filename.rfind('.')
  if pos == -1: return filename
  return filename[0:pos]

def ParseRequestPath(path):
  path = path.lower()
  if path.startswith("/"): path = path[1:]
  (path, query) = urllib.splitquery(path)
  if query is None: query = ""

  d = {}
  for kv in query.split('&'):
    if len(kv) == 0: continue
    epos = kv.find('=')
    if epos < 0:
      d[urllib.unquote(kv)] = True
    else:
      key = urllib.unquote(kv[0:epos])
      value = urllib.unquote(kv[epos+1:])
      d[key] = value

  return (path, d)

