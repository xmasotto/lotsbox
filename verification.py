import imaplib
import re

import urllib
import urllib2

def send_verification_email(opener, email, t, uid):
    data = {}
    data['is_xhr'] = "true"
    data['t'] = t
    data['email'] = email
    data['reason'] = "create_api_app"
    data['_subject_uid'] = uid

    headers = {}
    headers['origin'] = "https://www.dropbox.com"
    headers['referer'] = "https://www.dropbox.com/developers/apps/create"

    url = "https://www.dropbox.com/sendverifyemail"
    req = urllib2.Request(url, urllib.urlencode(data), headers)

    # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    r = opener.open(req)
    response = r.read()
    if response != "ok":
        print(response)

def get_verification_url(email):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('uiuclotsbox@gmail.com', 'Bagels12')
    mail.select('inbox')

    query = ""
    query += '(HEADER Subject "verify")'
    query += ' (HEADER To "%s")' % email
    query += ' (FROM "no-reply@dropbox.com")'
    result, data = mail.search(None, query)

    if result == 'OK':
        response = data[0].split()
        if len(response) > 0:
            response = mail.fetch(response[-1], "(RFC822)")
            body = response[1][0][1]

            i = body.find('href=3D"')
            i2 = body.find('">', i)
            return body[i+8:i2].replace("=\r\n", "")

        else:
            return None
    else:
        raise Exception("Could not connect")
