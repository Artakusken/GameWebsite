import json

from requests import get, post, delete
from werkzeug.security import generate_password_hash, check_password_hash

print(get('http://kmetgwent.ddns.net/api/v2/my_deck/constructor').json())


