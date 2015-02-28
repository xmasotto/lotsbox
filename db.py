from pymongo import MongoClient

def db_connect():
	return MongoClient('localhost', 27017).LotsBox

def add_box(db, uid, key, secret, token, fTypes, space):
	box_record = {}
	box_record["uid"] = uid
	box_record["key"] = key
	box_record["secret"] = secret
	box_record["token"] = token
	box_record["types"] = fTypes
	box_record["space"] = space
	db.boxes.insert(box_record)

def add_file(db, uid, path, fid, key, size):
	file_record = {}
	file_record["uid"] = uid
	file_record["key"] = key
	file_record["path"] = path
	file_record["fid"] = fid
	file_record["size"] = size
	db.files.insert(file_record)

def find_file(db, uid, path):
	query = {"uid" : uid, "path" : path}
	file_record = db.files.find_one(query)
	query = {"uid" : uid, "key" : file_record["key"]}
	box_record = db.boxes.find_one(query)
	fid = file_record["fid"]
	key = box_record["key"]
	secret = box_record["secret"]
	token = box_record["token"]
	return fid, key, secret, token
	
def get_box(db, uid, fType, size):
	query = {"uid" : uid, "fTypes" : fType, "space" : {"$gt": size}}
	return db.boxes.find_one(query)
