import mechanize
import cookielib
import urllib
import urllib2
import imaplib
import time
import bs4
import json
import random
import util

def monkeypatch_mechanize():
    """Work-around for a mechanize 0.2.5 bug. See: https://github.com/jjlee/mechanize/pull/58"""
    import mechanize
    if mechanize.__version__ < (0, 2, 6):
        from mechanize._form import SubmitControl, ScalarControl

        def __init__(self, type, name, attrs, index=None):
            ScalarControl.__init__(self, type, name, attrs, index)
            # IE5 defaults SUBMIT value to "Submit Query"; Firebird 0.6 leaves it
            # blank, Konqueror 3.1 defaults to "Submit".  HTML spec. doesn't seem
            # to define this.
            if self.value is None:
                if self.disabled:
                    self.disabled = False
                    self.value = ""
                    self.disabled = True
                else:
                    self.value = ""
            self.readonly = True

        SubmitControl.__init__ = __init__

#DEAL WITH VERIFICATION
def generateAccount(k=254):
    base_email = "uiuclotsbox@gmail.com"
    try:
        email = base_email
        for j in range(k - len(base_email)):
            last = email.index("@")
            i = random.randrange(0, last)
            email = email[:i] + "." + email[i:]

        password = "Bagels13"
        fname = "Varun"
        lname = "Berry"
        return DropboxAccount(email, password, fname, lname)
    except Exception:
        raise
        # print("email \"%s\" already in use" % email)
        # return generateAccount(k)

class DropboxAccount:
    def __init__(self, email, password, fname, lname):
        self.email = email
        self.password = password
        self.fname = fname
        self.lname = lname

        cj = cookielib.LWPCookieJar()

        self.br = self.init_browser()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self.br.set_cookiejar(cj)
        self.email = email

        try:
            self.create_account()
            self.verify_account()
            self.fetch_auth_info()
        except KeyError:
            raise Exception("email already in use")

    def init_browser(self):
        monkeypatch_mechanize()
        br = mechanize.Browser()

        # Browser options
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

        return br

    def create_account(self):
        self.br.open("https://www.dropbox.com/login")
        self.br.select_form(nr=2)
        self.br.form.set_value(self.fname, "fname")
        self.br.form.set_value(self.lname, "lname")
        self.br.form.set_value(self.email, name="email")
        self.br.form.set_value(self.password, "password")
        self.br.form.find_control("tos_agree").items[0].selected=True
        self.br.submit()

    def get_verification_url(self):
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('uiuclotsbox@gmail.com', 'Bagels12')
        mail.select('inbox')

        query = ""
        query += '(HEADER Subject "verify")'
        query += ' (HEADER To "%s")' % self.email
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

    def verify_account(self):
        # send verification email
        r = self.opener.open("https://www.dropbox.com/developers/apps/create")
        soup = bs4.BeautifulSoup(r.read())
        inputs = soup.find_all("form")[0].find_all("input")
        t = str(inputs[0]['value'])
        uid = int(inputs[1]['value'])

        req = urllib2.Request(
            "https://www.dropbox.com/sendverifyemail",
            urllib.urlencode({
                'is_xhr': "true",
                't': t,
                'email': self.email,
                '_subject_uid': uid,
                'reason': "create_api_app"
            }))
        r = self.opener.open(req)
        response = r.read()
        if response != "ok":
            raise Exception(response)

        # Poll IMAP server for verification url
        for i in range(10):
            print("trying...")
            url = self.get_verification_url()
            if url is not None:
                break
            time.sleep(1)
        else:
            raise Exception("Could not verify email!")

        self.br.open(url)
        print("verified!")

    def create_app(self, appname):
        self.br.open("https://www.dropbox.com/developers/apps/create")
        self.br.select_form(nr=0)
        self.br.form.set_value(["api"], name="app_type")
        self.br.form.set_value(["files"], name="data_type")
        self.br.form.set_value(["specific"], name="file_access")
        self.br.form.set_value(appname, name="name")
        for fType in range(3):
            self.br.form.find_control("file_types").items[fType].selected=True
        self.br.form.find_control("tos_accept").items[0].selected=True
        self.br.submit()

        project_url = "https://www.dropbox.com%s" % self.br.response().read()
        self.br.open(project_url)

        soup = bs4.BeautifulSoup(self.br.response().read())
        config = soup.find(id = "config-content").find_all('tr')
        app_key = config[6].find_all('div')[1].text
        app_secret = config[7].find_all('div')[1].text
        return app_key, app_secret

    def fetch_auth_info(self):
        appname = "lotsbox_" + util.random_characters(30)
        self.app_key, self.app_secret = self.create_app(appname)
        # get the oauth token
        soup = bs4.BeautifulSoup(self.br.response().read())
        app_id = soup.find_all("input", type="hidden")[2]['value']
        t = soup.find_all("input", type="hidden")[1]['value']

        req = urllib2.Request(
            "https://www.dropbox.com/developers/apps/generate_access_token",
            urllib.urlencode({
                'is_xhr': True,
                'app_id': app_id,
                't': t
            }))
        r = self.opener.open(req)
        self.app_token = json.loads(r.read())['token']
