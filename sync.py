import os
import shutil
import time

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

def apply_changes(old_folder, new_folder, changes):
    for op, filename in changes:
        old_file = os.path.join(old_folder, filename)
        new_file = os.path.join(new_folder, filename)

        if op == 'update_old':
            os.remove(old_file)
            shutil.copyfile(new_file, old_file)
            shutil.copystat(new_file, old_file)

        if op == 'add_old':
            dirname = os.path.dirname(old_file)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            shutil.copyfile(new_file, old_file)
            shutil.copystat(new_file, old_file)

        if op == 'update_new':
            os.remove(new_file)
            shutil.copyfile(old_file, new_file)
            shutil.copystat(old_file, new_file)

        if op == 'add_new':
            dirname = os.path.dirname(new_file)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            shutil.copyfile(old_file, new_file)
            shutil.copystat(old_file, new_file)

old_folder = "testfolder"
new_folder = "testfolder2"

while True:
    old_files = get_local_files(old_folder)
    new_files = get_local_files(new_folder)

    changes = track_changes(old_files, new_files)
    print(changes)
    apply_changes(old_folder, new_folder, changes)

    time.sleep(1)
