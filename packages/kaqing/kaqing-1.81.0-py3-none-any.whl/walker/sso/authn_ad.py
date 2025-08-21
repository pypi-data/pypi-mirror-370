import base64
import json
import re
import requests
from urllib.parse import urlparse, parse_qs

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

        roles = self.get_groups(id_token)
        roles.append(username)
        whitelisted = self.whitelisted_members()

        for role in roles:
            if role in whitelisted:
                return IdpLogin(redirect_url, id_token, state_token, username, session=session)

        contact = Config().get('idps.ad.contact', 'Please contact ted.tran@c3.ai.')
        log2(f'{username} is not whitelisted. {contact}')

        return None

    def extract_config_object(self, text: str):
        for line in text.split('\n'):
            groups = re.match(r'.*\$Config=\s*(\{.*)', line)
            if groups:
                js = groups[1].replace(';', '')
                config = json.loads(js)

                return config

        return None

    def whitelisted_members(self) -> list[str]:
        members_f = "/kaqing/members"
        try:
            with open(members_f, 'r') as file:
                lines = file.readlines()
            lines = [line.strip() for line in lines]

            def is_non_comment(line: str):
                return not line.startswith('#')

            lines = list(filter(is_non_comment, lines))

            return [line.split('#')[0].strip(' ') for line in lines]
        except FileNotFoundError:
            pass

        return []

    def get_groups(self, id_token: str) -> list[str]:
        def decode_jwt_part(encoded_part):
            missing_padding = len(encoded_part) % 4
            if missing_padding:
                encoded_part += '=' * (4 - missing_padding)
            decoded_bytes = base64.urlsafe_b64decode(encoded_part)
            return json.loads(decoded_bytes.decode('utf-8'))

        parts = id_token.split('.')
        # header = decode_jwt_part(parts[0])
        payload = decode_jwt_part(parts[1])

        if 'groups' in payload:
            return payload['groups']

        return []