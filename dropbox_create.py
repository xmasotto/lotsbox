import mechanize
import cookielib
import random
import bs4

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

def set_up_browser():
    monkeypatch_mechanize()
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    #br.set_debug_http(True)
    #br.set_debug_redirects(True)
    #br.set_debug_responses(True)

    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    return br

def get_cookie_jar(br):
    return br._ua_handlers['_cookies'].cookiejar

def create_dropbox(br, fname, lname, email, password):
    br.open("https://www.dropbox.com/login")
    br.select_form(nr=2)
    br.form.set_value(fname, "fname")
    br.form.set_value(lname, "lname")
    br.form.set_value(email, name="email")
    br.form.set_value(password, "password")
    br.form.find_control("tos_agree").items[0].selected=True
    br.submit()

def create_app(br, appname, fileTypes=[0, 1, 2]):
    br.open("https://www.dropbox.com/developers/apps/create")
    br.select_form(nr=0)
    br.form.set_value(["api"], name="app_type")
    br.form.set_value(["files"], name="data_type")
    br.form.set_value(["specific"], name="file_access")
    br.form.set_value(appname, name="name")
    for type in fileTypes:
        br.form.find_control("file_types").items[type].selected=True
    br.form.find_control("tos_accept").items[0].selected=True
    br.submit()

    project_url = "https://www.dropbox.com%s" % br.response().read()
    br.open(project_url)

    soup = bs4.BeautifulSoup(br.response().read())
    config = soup.find(id = "config-content").find_all('tr')
    app_key = config[6].find_all('div')[1].text
    app_secret = config[7].find_all('div')[1].text
    return app_key, app_secret
