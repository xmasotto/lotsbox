from pymongo import MongoClient

class LotsBoxDB:
    def __init__(self, host):
        self.db = MongoClient(host, 27017).LotsBox

    def add_box(self, uid, email, key, token, space):
        box_record = {}
        box_record["uid"] = uid
        box_record["key"] = key
        box_record["token"] = token
        box_record["space"] = space
        box_record["email"] = email
        self.db.boxes.insert(box_record)

    def add_space(self, key, space):
        box = self.db.boxes.find_one({"key" : key})
        print "Adding space: " + str(box["space"]) + " -----> " + str(box["space"] + space)
        self.db.boxes.update({"key" : key}, {"$set": {"space" : space + box["space"]}})

    def remove_space(self, key, space):
        box = self.db.boxes.find_one({"key" : key})
        print "Removing space: " + str(box["space"]) + " -----> " + str(box["space"] - space)
        self.db.boxes.update({"key" : key}, {"$set": {"space" : box["space"] - space}})

    def add_file(self, uid, path, fid, key, size, mod_time):
        file_record = {}
        file_record["uid"] = uid
        file_record["key"] = key
        file_record["path"] = path
        file_record["fid"] = fid
        file_record["size"] = size
        file_record["mod_time"] = mod_time
        self.db.files.insert(file_record)
        self.remove_space(key, size)

    def delete_file(self, fid):
        file_record = self.db.files.find_one({"fid" : fid})
        key = file_record["key"]
        size = file_record["size"]
        self.db.files.remove({'fid': fid})
        self.add_space(key, size)

    def list_files(self, uid):
        result = []
        query = {"uid": uid}
        for doc in self.db.files.find(query):
            result.append((doc["path"], doc["mod_time"]))
        return result


    def find_file(self, uid, path):
        query = {"uid" : uid, "path" : path}
        file_record = self.db.files.find_one(query)
        #CHECK THAT FILE RECORD EXISTS
        query = {"uid" : uid, "key" : file_record["key"]}
        box_record = self.db.boxes.find_one(query)
        fid = file_record["fid"]
        mod_time = file_record["mod_time"]
        token = box_record["token"]
        return fid, mod_time, token

    def get_file_path(self, fid):
        file_record = self.db.files.find_one({"fid" : fid})
        fid = file_record["fid"]
        path = file_record["path"]
        return path

    def is_unique_fid(self, fid):
        return None == self.db.files.find_one({"fid" : fid})

    def get_box(self, uid, size):
        print "Looking for box with more than: " + str(size)
        query = {"uid" : uid, "space" : {"$gt": size}}
        box_record = self.db.boxes.find_one(query)
        if box_record:
            print "Box found!"
            key = box_record["key"]
            token = box_record["token"]
            return key, token
        else:
            print "No box found :("
            return None

mydb = LotsBoxDB("ec2-52-10-40-186.us-west-2.compute.amazonaws.com")
