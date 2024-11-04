from flask import session
from errors import ApplicationException
from uuid import uuid4
import os

users = [
    {'username':os.getenv('ADMIN_USERNAME'), 'roles':['admin', 'user']},
    {'username':'support', 'roles':['user']},
]

class UserNotFoundException(ApplicationException):
    code = "618552"
    def __init__(self,username):
        super().__init__("User "+username+" not found")
        self.id="{0}-{1}".format(self.code, uuid4())

# def auth(username, password):
    # TODO implement call to auth API in the backend

def getByUsername(username):
    user_entry = next((user for user in users if user['username'] == username), None)

    if user_entry is None:
        raise UserNotFoundException(username)
    
    session.update(user_entry)

    return user_entry
