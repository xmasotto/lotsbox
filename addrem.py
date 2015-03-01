import dropbox
import os
import util
from db import *
from dropbox_account import *

db = LotsBoxDB()

def generate_fid(uid):
    fid = util.random_characters(10)
    while not db.is_unique_fid(fid):
        fid = util.random_combination(10)
    return fid

def add_file(uid, input_file, path, size, mod_time):
    #CHECK FILE SIZE > 2GB
    box = db.get_box(uid, size)
    if box == None:
        account = generateAccount()
        box = account.app_key, account.app_token
        db.add_box(uid, account.app_key, account.app_token, 4**30)
    fid = generate_fid(uid)

    client = dropbox.client.DropboxClient(box[1])
    print("put in " + fid)
    client.put_file(fid, open(input_file, "r"))
    db.add_file(uid, path, fid, box[0], size, mod_time) #UPDATE BOX SIZE IN ADD_FILE
    print("added file: %s" % path)

def delete_file(uid, path):
    fid, mod_time, token = db.find_file(uid, path)
    db.delete_file(fid)
    client = dropbox.client.DropboxClient(token)
    client.file_delete(fid)

    print("deleted file: %s" % path)

def download_file(uid, path, output_file):
    fid, mod_time, token = db.find_file(uid, path)
    path = db.get_file_path(fid)
    client = dropbox.client.DropboxClient(token)

    output = open(output_file, "w")
    output.write(client.get_file(fid).read())
    output.close()

    # update times
    atime = os.stat(output_file).st_atime
    os.utime(output_file, (atime, mod_time))

    print("downloaded file: %s" % path)
