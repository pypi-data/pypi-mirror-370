import base64
import json
import requests

class IdpLogin:
    def __init__(self, app_login_url: str, id: str, state: str, user: str = None, session: requests.Session = None):
        self.app_login_url = app_login_url
        self.id = id
        self.state = state
        self.user = user
        self.session = session

    def deser(idp_token: str):
        j = json.loads(base64.b64decode(idp_token.encode('utf-8')))

        return IdpLogin(j['r'], j['id'], j['state'])

    def ser(self):
        return base64.b64encode(json.dumps({
            'r': self.app_login_url,
            'id': self.id,
            'state': self.state
        }).encode('utf-8')).decode('utf-8')

    def shell_user(self):
        if not self.user:
            return None

        return self.user.split('@')[0].replace('.', '')