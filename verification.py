import imaplib
import re

import urllib
import urllib2

def send_verification_email(cj, email, t, uid):
    data = {}
    data['is_xhr'] = True
    data['t'] = t
    data['email'] = email
    data['reason'] = "create_api_app"
    data['_subject_uid'] = uid

    headers = {}
    headers['origin'] = "https://www.dropbox.com"
    headers['referer'] = "https://www.dropbox.com/developers/apps/create"

    url = "https://www.dropbox.com/sendverifyemail"
    req = urllib2.Request(url, urllib.urlencode(data), headers)

    opener = urllib.build_opener(urllib2.HTTPCookieProcessor(cj))
    r = opener.open(url, urllib.urlencode(data), headers)
    response = r.read()
    if response != "ok":
        print(response)

def get_verification_url():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('uiuclotsbox@gmail.com', 'Bagels12')
    mail.select('inbox')
    result, data = mail.search(
        None, '(HEADER Subject "verify") (FROM "no-reply@dropbox.com")')
    if result == 'OK':
        response = data[0].split()
        if len(response) > 0:
            response = mail.fetch(response[-1], "(RFC822)")
            body = response[1][0][1]

            i = body.find('href=3D"')
            i2 = body.find('">', i)
            return body[i+7:i2+1].replace("=\r\n", "")

        else:
            raise Exception("No results found")
    else:
        raise Exception("Could not connect")
