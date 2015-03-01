import random
import datetime

def random_characters(r):
    pool = [chr(ord('A') + x) for x in range(26)] + [str(x) for x in range(10)]
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return "".join(pool[i] for i in indices)

# ($ICON_NAME, $PATH, $EPOCH_SEC, $LINK) ->
# ($ICON_NAME, $PATH, $FILE_KIND, $LAST_MODIFIED_DATE_TIME, $LINK)
def get_formatted_file_list(raw_file_list):
  new_file_list = []

  for f in raw_file_list:
    path = f[1]
    epoch = f[2]

    date_time = datetime.datetime.fromtimestamp(epoch).strftime('%m/%d/%Y %I:%M:%S %p').lstrip('0')
    kind = get_file_kind(path)

    new_file_list.append((f[0], path, kind, date_time, f[3]))

  return new_file_list

def get_file_kind(path):
  kind = 'file'

  if path[-1] == '/':
    kind = 'folder'
  else:
    if '.' in path:
      extension = path[path.rfind('.'):]
      if extension == '.pdf' or extension == '.doc' or extension == '.docx':
        kind = 'document'
      elif extension == '.zip' or extension == '.rar' or extension == '.tar':
        kind = 'archive'

  return kind