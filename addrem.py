import dropbox
import os
import util
from db import *
from dropbox_account import *

size_buffer = (2**10) * 500
#start_space = 2**30
start_space = (2**20)*100

def generate_fid(uid):
    fid = util.random_characters(10)
    while not mydb.is_unique_fid(fid):
        fid = util.random_combination(10)
    return fid

def add_file(uid, input_file, path, size, mod_time):
    #CHECK FILE SIZE > 150MB
    box = mydb.get_box(uid, size + size_buffer)
    if box == None:
        account = generateAccount()
        box = account.app_key, account.app_token
        mydb.add_box(uid,
                     account.email,
                     account.app_key,
                     account.app_token,
                     start_space)
    fid = generate_fid(uid)

    client = dropbox.client.DropboxClient(box[1])
    print("put in " + fid)
    client.put_file(fid, open(input_file, "r"))
    mydb.add_file(uid, path, fid, box[0], size, mod_time)
    print("added file: %s" % path)

def delete_file(uid, path):
    fid, mod_time, token = mydb.find_file(uid, path)
    mydb.delete_file(fid)
    client = dropbox.client.DropboxClient(token)
    client.file_delete(fid)

    print("deleted file: %s" % path)

def download_file(uid, path, output_file):
    fid, mod_time, token = mydb.find_file(uid, path)
    path = mydb.get_file_path(fid)
    client = dropbox.client.DropboxClient(token)

    output = open(output_file, "w")
    output.write(client.get_file(fid).read())
    output.close()

    # update times
    atime = os.stat(output_file).st_atime
    os.utime(output_file, (atime, mod_time))

    print("downloaded file: %s" % path)
