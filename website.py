from flask import Flask, render_template, request
from db import *

import urllib2
import sys
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
  return "/?uid=%s&p=%s" % (uid, path + name)

@app.route('/')
def main(path=None):
  uid = request.args.get('uid')
  if uid == None:
    return sign_in()
  else:
    path = request.args.get('p') or ""
    if path == "" or path[-1] == '/':
      return show_folder(uid, path)
    else:
      return show_file(uid, path)


def show_file(uid, path):
  pass


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
