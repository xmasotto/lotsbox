from pymongo import MongoClient

class LotsBoxDB:
    def __init__(self):
        self.db = MongoClient('localhost', 27017).LotsBox

    def add_box(uid, key, secret, token, space):
        box_record = {}
        box_record["uid"] = uid
        box_record["key"] = key
        box_record["secret"] = secret
        box_record["token"] = token
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
        #CHECK THAT FILE RECORD EXISTS
        query = {"uid" : uid, "key" : file_record["key"]}
        box_record = self.db.boxes.find_one(query)
        fid = file_record["fid"]
        key = box_record["key"]
        secret = box_record["secret"]
        token = box_record["token"]
        return fid, key, secret, token
    
    def find_file(fid):
        file_record = self.db.files.find_one({"fid" : fid})
        box_record = self.db.boxes.find_one({"fid" : file_record["key"]})
        fid = file_record["fid"]
        path = file_record["path"]
        token = box_record["token"]
        return fid, path, token
    
    def is_unique_fid(fid):
        return None == self.db.files.find_one({"fid" : fid})
        
    def get_box(uid, size):
        query = {"uid" : uid, "space" : {"$gt": size}}
        box_record = self.db.boxes.find_one(query)
        key = box_record["key"]
        secret = box_record["secret"]
        token = box_record["token"]
        return key, secret, token
