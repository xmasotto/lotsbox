from dropbox_create import *
from verification import *

import cookielib
import bs4
import time

email = ".uiuclots.box@gmail.com"

br = set_up_browser()
create_dropbox(br, "test", "test2", email, "Bagels12")
cj = get_cookie_jar(br)

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
r = opener.open("https://www.dropbox.com/developers/apps/create")
soup = bs4.BeautifulSoup(r.read())

open("hello.html", "w").write(str(soup))

inputs = soup.find_all("form")[0].find_all("input")
t = str(inputs[0]['value'])
uid = int(inputs[1]['value'])
send_verification_email(opener, email, t, uid)

# poll verification url
for i in range(10):
    print("trying...")
    url = get_verification_url(email)
    if url is not None:
        break
    time.sleep(1)

# open the verification url
br.open(url)

print("verified")

app_key, app_secret = create_app(br, email + "nohomo")
print(app_key, app_secret)

soup = bs4.BeautifulSoup(br.response().read())
app_id = soup.find_all("input", type="hidden")[2]['value']
t = soup.find_all("input", type="hidden")[1]['value']

data = {}
data['is_xhr'] = "true"
data['app_id'] = app_id
data['t'] = t

headers = {}
# headers['origin'] = "https://www.dropbox.com"
# headers['referer'] = "https://www.dropbox.com/developers/apps/create"

url = "https://www.dropbox.com/developers/apps/generate_access_token"
req = urllib2.Request(url, urllib.urlencode(data), headers)

r = opener.open(req)
response = r.read()
if response != "ok":
    print(response)
