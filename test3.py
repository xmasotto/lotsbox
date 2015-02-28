from dropbox import *
import random

def mutate_email(email):
    last = base_email.index("@")
    for l in range(5):
        i = random.randrange(0, last)
        j = random.randint(1, 5)
        email = email[:i] + "." * j + email[i:]
    return email

# generate an email and a dropbox account
base_email = "uiuclotsbox@gmail.com"
while True:
    email = mutate_email(base_email)
    try:
        account = DropboxAccount(email, "Bagels13", "varun", "berry")
        break
    except Exception:
        pass

print(account.app_key)
print(account.app_secret)
print(account.app_token)
