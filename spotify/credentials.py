from os import environ as env
from varenv import load_vars


load_vars()
CLIENT_ID = env["CLIENT_ID"]
CLIENT_SECRET = env["CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8000/spotify/redirect/"
