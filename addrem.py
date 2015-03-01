import dropbox
import os
from db import *
from dropbox_account import *

db = LotsBoxDB()

def random_combination(iterable , r):
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return tuple(pool[i] for i in indices)

def generate_fid(uid):
    chars = [chr(ord('A') + x) for x in range(26))] + [str(x) for x in range(10)]
    fid = random_combination(chars, 10)
    while not db.is_unique_fid(fid):
        fid = random_combination(chars, 10)
    return fid


def add_file(uid, path, mod_time):
    #CHECK FILE SIZE > 2GB
    size = os.path.getsize(path)
    box = db.get_box(uid, size)
    if box == None:
        account = generateAccount() #CHECK FOR EMAIL CONFLICTS
        box = account.app_key, account.app_secret, account.app_token
        db.add_box(uid, app_key, app_secret, app_token, 4**30) #NEED EXACT SPACE SIZE   
    fid = generate_fid()
    f = read(path, "r")
    client = dropbox.client.DropboxClient(box[2])
    client.put_file(fid, f)
    f.close()
    db.add_file(uid, path) #UPDATE BOX SIZE IN ADD_FILE
    
def delete_file(uid, path):
    fid, key, secret, token = db.find_file(uid, path)
    client = dropbox.client.DropboxClient(token)
    client.file_delete(fid)
    
def download_file(fid):
    fid, path, token = db.find_file(fid)
    client = dropbox.client.DropboxClient(token)
    
    #SAVE FILE TO CORRECT NAME AND PLACE
    f = open(fid, "w")
    f.write(client.get_file(fid).read())
    f.close()
