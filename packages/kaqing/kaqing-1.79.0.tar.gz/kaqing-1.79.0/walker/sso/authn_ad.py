import json
import re
import requests
from urllib.parse import urlparse, parse_qs, unquote

from walker.sso.authenticator import Authenticator

from .idp_login import IdpLogin
from walker.config import Config
from walker.utils import log2

class AdAuthenticator(Authenticator):
    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(AdAuthenticator, cls).__new__(cls)

        return cls.instance

    def authenticate(self, idp_uri: str, app_host: str, username: str, password: str) -> IdpLogin:
        # https%3A%2F%2Fplat.c3ci.cloud%2Fc3%2Fc3%2Foidc%2Flogin
        parsed_url = urlparse(idp_uri)
        query_string = parsed_url.query
        params = parse_qs(query_string)
        state_token = params.get('state', [''])[0]
        redirect_url = params.get('redirect_uri', [''])[0]

        session = requests.Session()
        r = session.get(idp_uri)
        if Config().is_debug():
            log2(f'{r.status_code} {idp_uri}')
        # print(r.text)

        # extract_config_object('$Config={"fShowPersistentCookiesWarning":false}\n//]]></script>')
        config = self.extract_config_object(r.text)

        login = f'https://login.microsoftonline.com/53ad779a-93e7-485c-ba20-ac8290d7252b/login';
        body = {
            'login': username,
            'LoginOptions': '3',
            'passwd': password,
            'ctx': config['sCtx'],
            'hpgrequestid': config['sessionId'],
            'flowToken': config['sFT']
        }
        # print(body)
        r = session.post(login, data=body, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        if Config().is_debug():
            log2(f'{r.status_code} {login}')
        # print(r.text)

        config = self.extract_config_object(r.text)

        kmsi = 'https://login.microsoftonline.com/kmsi'
        body = {
            'LoginOptions': '1',
            'ctx': config['sCtx'],
            'hpgrequestid': config['sessionId'],
            'flowToken': config['sFT'],
        }
        r = session.post(kmsi, data=body, headers={
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        if Config().is_debug():
            log2(f'{r.status_code} {kmsi}')

        id_token = None
        if (config := self.extract_config_object(r.text)):
            if 'strServiceExceptionMessage' in config:
                log2(config['strServiceExceptionMessage'])
            else:
                log2('Unknown err.')

            return None

        id_token = self.extract(r.text, r'.*name=\"id_token\" value=\"(.*?)\".*')

        members_f = "/kaqing/members"
        try:
            with open(members_f, 'r') as file:
                lines = file.readlines()
            lines = [line.strip() for line in lines]
            if username in lines:
                return IdpLogin(redirect_url, id_token, state_token, username, session=session)
        except FileNotFoundError:
            pass

        log2(f'{username} is not whitelisted. Please contact henry.wong@c3.ai.')

        return None

    def extract_config_object(self, text: str):
        for line in text.split('\n'):
            groups = re.match(r'.*\$Config=\s*(\{.*)', line)
            if groups:
                js = groups[1].replace(';', '')
                config = json.loads(js)

                # print("* sessionId =", config['sessionId'])
                # print("* ctx =", config['sCtx'])
                # print("* flowToken =", config['sFT'])

                return config

        return None