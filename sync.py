#!/usr/bin/env python

import sys
import os
import shutil
import time

from addrem import *

MY_UID = 74

def get_local_files(path):
    result = []
    for dirpath, dirname, filenames in os.walk(path):
        for name in filenames:
            localpath = os.path.join(dirpath, name)
            mtime = os.stat(localpath).st_mtime
            result.append((localpath[len(path)+1:], mtime))
    return result

def track_changes(old_files, new_files):
    result = []

    new_files_set = set(name for name, mtime in new_files)
    old_files_set = set(name for name, mtime in old_files)

    # add/update to old
    for name, mtime in old_files:
        for name2, mtime2 in new_files:
            if name == name2:
                if mtime > mtime2:
                    result.append(('update_new', name))
                break
        else:
            result.append(('add_new', name))


    # add/update to new
    for name, mtime in new_files:
        for name2, mtime2 in old_files:
            if name == name2:
                if mtime > mtime2:
                    result.append(('update_old', name))
                break
        else:
            result.append(('add_old', name))

    return result

def apply_changes(local_folder, changes):
    for op, filename in changes:
        local_file = os.path.join(local_folder, filename)

        if op == 'update_old':
            # download a file from dropbox (update existing)
            os.remove(local_file)
            download_file(MY_UID, filename, local_file)

        if op == 'add_old':
            # download a file from dropbox (add new)
            download_file(MY_UID, filename, local_file)

        if op == 'update_new':
            # upload a file to dropbox (update existing)
            size = os.path.getsize(local_file)
            mod_time = os.stat(local_file).st_mtime
            delete_file(MY_UID, filename)
            add_file(MY_UID, local_file, filename, size, mod_time)

        if op == 'add_new':
            size = os.path.getsize(local_file)
            mod_time = os.stat(local_file).st_mtime
            add_file(MY_UID, local_file, filename, size, mod_time)

def main(argv):
    if len(argv) != 3:
        print("Usage: " + argv[0] + " uid sync_folder")
        sys.exit(1)

    global MY_UID
    MY_UID = argv[1]
    local_folder = argv[2]

    while True:
        local_files = get_local_files(local_folder)
        server_files = db.list_files(MY_UID)

        changes = track_changes(local_files, server_files)
        print(changes)
        apply_changes(local_folder, changes)

        time.sleep(1)

if __name__ == "__main__":
    main(sys.argv)
