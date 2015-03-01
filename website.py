from flask import Flask, render_template
import urllib2
import sys
app = Flask(__name__)

icons = dict()

def get_icon(name):
  p = name.rfind(".")
  if p == -1:
    "http://icons.iconarchive.com/icons/danrabbit/elementary/32/Folder-icon.png"
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


# example file data
file_list = [(u'testfolder/.DS_Store', 1425166227.0),
 (u'testfolder/a copy 10.txt', 1425163704.0),
 (u'testfolder/a copy 11.txt', 1425163704.0),
 (u'testfolder/a copy 2.txt', 1425163682.0),
 (u'testfolder/a copy 3.txt', 1425163698.0),
 (u'testfolder/a copy 4.txt', 1425163698.0),
 (u'testfolder/a copy 5.txt', 1425163698.0),
 (u'testfolder/a copy 6.txt', 1425163704.0),
 (u'testfolder/a copy 7.txt', 1425163704.0),
 (u'testfolder/a copy 8.txt', 1425163704.0),
 (u'testfolder/a copy 9.txt', 1425163704.0),
 (u'testfolder/a copy.txt', 1425163675.0),
 (u'testfolder/a.txt', 1425163562.0),
 (u'testfolder/e copy 10.txt', 1425163704.0),
 (u'testfolder/e copy 11.txt', 1425163704.0),
 (u'testfolder/e copy 12.txt', 1425163729.0),
 (u'testfolder/e copy 13.txt', 1425163704.0),
 (u'testfolder/e copy 14.txt', 1425163698.0),
 (u'testfolder/e copy 15.txt', 1425163698.0),
 (u'testfolder/e copy 16.txt', 1425163698.0)]

f_list = list()
for f in file_list:
  f_list.append((get_icon(f[0]), f[0], f[1]))  #"\"" 
file_list = f_list


@app.route('/')
def main():
  files = list()
  return render_template('main.html', messages=file_list)

@app.route('/signin')
def sign_in():
  return render_template('sign_in.html')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
