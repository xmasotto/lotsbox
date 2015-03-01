from flask import Flask, render_template, request, Response
from db import *
from addrem import *

import urllib2
import sys
import dropbox
import mimetypes
import util
import random

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

def get_stats(uid):
  remaining = 0
  total = 0
  boxes = mydb.db.boxes.find({"uid": uid})
  for box in boxes:
    print(box)
    remaining += box['space']
    total += start_space
  used = total - remaining
  if total == 0:
      total = 100 * 1024 * 1024
  return round(used / 1024 / 1024, 1), round(total / 1024 / 1024, 1)

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

def htmlcolor(r, g, b):
    def _chkarg(a):
        if isinstance(a, int): # clamp to range 0--255
            if a < 0:
                a = 0
            elif a > 255:
                a = 255
        elif isinstance(a, float): # clamp to range 0.0--1.0 and convert to integer 0--255
            if a < 0.0:
                a = 0
            elif a > 1.0:
                a = 255
            else:
                a = int(round(a*255))
        else:
            raise ValueError('Arguments must be integers or floats.')
        return a
    r = _chkarg(r)
    g = _chkarg(g)
    b = _chkarg(b)
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)


@app.route('/analytics')
def analytics():
  uid = request.args.get('uid')
  if uid == None:
    return sign_in()
  else:
    file_list = mydb.list_files(uid)
    box_info = [(box['email'], round(box['space'] / 1024 / 1024, 1))
             for box in mydb.db.boxes.find({"uid": uid})]
    boxes = []
    for box in box_info:
      boxes.append(("Box " + str(len(boxes)+1), round(start_space/1024/1024, 1) - box[1], htmlcolor(random.randint(0, 100), random.randint(100, 255), random.randint(100, 255))))
    return render_template("analytics.html",
                           uid=uid,
                           boxes=boxes,
                           num_boxes=len(box_info),
                           num_files=len(file_list),
                           stats=get_stats(uid))

@app.route('/accounts')
def accounts():
  uid = request.args.get('uid')
  if uid == None:
    return sign_in()
  else:
    file_list = mydb.list_files(uid)
    box_size = round(start_space/1024/1024, 1)
    boxes = [(box['email'], box_size - round(box['space'] / 1024 / 1024, 1))
             for box in mydb.db.boxes.find({"uid": uid})]
    return render_template("accounts.html",
                           uid=uid,
                           num_files=len(file_list),
                           boxes=boxes,
                           box_size=box_size,
                           stats=get_stats(uid))

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

  file_list2 = [(name[len(path):], mod_time)
               for name, mod_time in file_list
               if name.startswith(path)]

  files = {}
  for filename, mod_date in file_list2:
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

  return render_template('main.html',
                         messages=formatted_data,
                         uid=uid,
                         num_files=len(file_list),
                         stats=get_stats(uid))

def sign_in():
  return render_template('sign_in.html')

if __name__ == '__main__':
  port = 5000
  if len(sys.argv) > 1:
    port = int(sys.argv[1])

  app.run(debug=True, host='0.0.0.0', port=port)
