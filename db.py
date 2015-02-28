from pymongo import MongoClient

class LotsBoxDB:
	def __init__(self):
		self.db = MongoClient('localhost', 27017).LotsBox

	def add_box(uid, key, secret, token, fTypes, space):
		box_record = {}
		box_record["uid"] = uid
		box_record["key"] = key
		box_record["secret"] = secret
		box_record["token"] = token
		box_record["types"] = fTypes
		box_record["space"] = space
		self.db.boxes.insert(box_record)

	def add_file(uid, path, fid, key, size):
		file_record = {}
		file_record["uid"] = uid
		file_record["key"] = key
		file_record["path"] = path
		file_record["fid"] = fid
		file_record["size"] = size
		self.db.files.insert(file_record)

	def find_file(uid, path):
		query = {"uid" : uid, "path" : path}
		file_record = self.db.files.find_one(query)
		query = {"uid" : uid, "key" : file_record["key"]}
		box_record = self.db.boxes.find_one(query)
		fid = file_record["fid"]
		key = box_record["key"]
		secret = box_record["secret"]
		token = box_record["token"]
		return fid, key, secret, token
		
	def get_box(uid, fType, size):
		query = {"uid" : uid, "fTypes" : fType, "space" : {"$gt": size}}
		box_record = self.db.boxes.find_one(query)
		key = box_record["key"]
		secret = box_record["secret"]
		token = box_record["token"]
		return key, secret, token
