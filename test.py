from dropbox_create import *
from verification import *

br = set_up_browser()
create_dropbox(br, "test", "test2", "...uiuclotsbox@gmail.com", "Bagels12")
get_cookie_jar(br).save('cookie_file')
