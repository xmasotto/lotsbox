from dropbox_account import *
import random

account = generateAccount()

print(account.app_key)
print(account.app_secret)
print(account.app_token)
