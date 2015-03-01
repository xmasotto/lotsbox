from flask import Flask, render_template, request
from db import *

app = Flask(__name__)

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

  return render_template('main.html', messages=list(files.items()))

def sign_in():
  return render_template('sign_in.html')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
