import dropbox
import os
from db import *
from dropbox_account import *

db = LotsBoxDB()

#NEED TO DEAL WITH FILE TYPES
def generate_types(fType):
	types = [0, 1]
		if fType in types:
			types.append(2)
		else:
			types.append(fType)
	return types
	
#NEED TO DEAL WITH FILE TYPES
def get_type(path):
	return 0

#NEED TO GENERATE UNIQUE FID
def generate_fid():
	return str(random.randint(1, 1000)
	

def add_file(uid, path, mod_time):
	fType = get_type(path)
	size = os.path.getsize(path)
	box = db.get_box(uid, fType, size)
	if box == None:
		types = generate_types(0)
		account = generateAccount(types) #CHECK FOR EMAIL CONFLICTS
		box = account.app_key, account.app_secret, account.app_token
		db.add_box(uid, app_key, app_secret, app_token, types, 4**30) #NEED EXACT SPACE SIZE
	f = read(path, "r")
	client = dropbox.client.DropboxClient(box[2])
	fid = generate_fid()
	client.put_file(fid, f)
	db.add_file(uid, path) #UPDATE BOX SIZE IN ADD_FILE
	
def delete_file(uid, path):
	fid, key, secret, token = find_file(uid, path)
	client = dropbox.client.DropboxClient(token)
	client.file_delete(fid)
	
