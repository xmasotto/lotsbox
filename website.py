from flask import Flask, render_template, request, Response
from db import *

import urllib2
import sys
import dropbox
import mimetypes
import util

app = Flask(__name__)

icons = {}
def get_icon(name):
  p = name.rfind(".")
  if name[-1] == "/":
    return "http://icons.iconarchive.com/icons/danrabbit/elementary/32/Folder-icon.png"
  ext = name[p+1:]
  if ext in icons:
    return icons[ext]
  url = "http://icons.iconarchive.com/icons/fatcow/farm-fresh/32/file-extension-"+ext+"-icon.png"
  try:
    urllib2.urlopen(url)
    icons[ext] = url
    return url
  except Exception:
    print "Unexpected error:", sys.exc_info()
    if ext in ['xml', 'py', 'cpp', 'c', 'php', 'js', 'html']:
      return "http://icons.iconarchive.com/icons/danrabbit/elementary/32/Document-xml-icon.png"
    else:
      return "http://icons.iconarchive.com/icons/danrabbit/elementary/32/Document-empty-icon.png"

def get_link(uid, path, name):
  return "/%s?uid=%s" % (path + name, uid)

@app.route('/')
@app.route('/<path:path>')
def main(path=""):
  uid = request.args.get('uid')
  if uid == None:
    return sign_in()
  else:
    if path == "" or path[-1] == '/':
      return show_folder(uid, path)
    else:
      return show_file(uid, path)

@app.route('/analytics')
def analytics():
  return render_template("analytics.html")  

def show_file(uid, path):
  fid, mod_time, token = mydb.find_file(uid, path)
  client = dropbox.client.DropboxClient(token)
  mime = mimetypes.guess_type(path)[0]
  mime = mime or "application/octet-stream"

  response = client.get_file(fid)

  def gen():
    while True:
      data = response.read(1000 * 1000)
      if data:
        yield data
      else:
        break

  headers = {
    'Content-length': response.getheader('content-length')
  }

  return Response(gen(), headers=headers, mimetype=mime)


def show_folder(uid, path):
  file_list = mydb.list_files(uid)
  local_file_list = []

  file_list = [(name[len(path):], mod_time)
               for name, mod_time in file_list
               if name.startswith(path)]

  files = {}
  for filename, mod_date in file_list:
    if '/' in filename:
      filename = filename[:filename.index('/')+1]
      if filename in files:
        files[filename] = max(mod_date, files[filename])
      else:
        files[filename] = mod_date
    else:
      files[filename] = mod_date

  data = [(get_icon(name), name, mod_time, get_link(uid, path, name)) for name, mod_time in files.items()]
  formatted_data = util.get_formatted_file_list(data)

  return render_template('main.html', messages=formatted_data)

def sign_in():
  return render_template('sign_in.html')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
