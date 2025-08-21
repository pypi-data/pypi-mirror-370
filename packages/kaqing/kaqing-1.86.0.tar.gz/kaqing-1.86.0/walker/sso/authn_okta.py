import json
import jwt
import requests
from urllib.parse import urlparse, parse_qs, unquote

from walker.sso.authenticator import Authenticator

from .idp_login import IdpLogin
from walker.config import Config
from walker.utils import log2

class OktaAuthenticator(Authenticator):
    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(OktaAuthenticator, cls).__new__(cls)

        return cls.instance

    def authenticate(self, idp_uri: str, app_host: str, username: str, password: str) -> IdpLogin:
        parsed_url = urlparse(idp_uri)
        query_string = parsed_url.query
        params = parse_qs(query_string)
        state_token = params.get('state', [''])[0]
        redirect_url = params.get('redirect_uri', [''])[0]

        okta_host = parsed_url.hostname

        url = f"https://{okta_host}/api/v1/authn"
        payload = {
            "username": username,
            "password": password,
            "options": {
                "warnBeforePasswordExpired": True,
                "multiOptionalFactorEnroll": False
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        session = requests.Session()
        response = session.post(url, headers=headers, data=json.dumps(payload))
        if Config().is_debug():
            log2(f'{response.status_code} {url}')
        auth_response = response.json()

        if 'sessionToken' not in auth_response:
            return None

        session_token = auth_response['sessionToken']

        url = f'{idp_uri}&sessionToken={session_token}'
        r = session.get(url)
        if Config().is_debug():
            log2(f'{r.status_code} {url}')

        id_token = OktaAuthenticator().extract(r.text, r'.*name=\"id_token\" value=\"(.*?)\".*')
        if not id_token:
            err = OktaAuthenticator().extract(r.text, r'.*name=\"error_description\" value=\"(.*?)\".*')
            if err:
                log2(unquote(err).replace('&#x20;', ' '))
            else:
                log2('id_token not found\n' + r.text)

            return None

        if group := Config().get('app.login.admin-group', '{host}/C3.ClusterAdmin').replace('{host}', app_host):
            if group not in OktaAuthenticator.get_groups(okta_host, id_token):
                tks = group.split('/')
                group = tks[len(tks) - 1]
                log2(f'{username} is not a member of {group}.')

                return None

        return IdpLogin(redirect_url, id_token, state_token, username, session=session)

    def get_groups(idp_host, id_token) -> list[str]:
        groups: list[str] = []

        if not jwt.algorithms.has_crypto:
            log2("No crypto support for JWT, please install the cryptography dependency")

            return groups

        okta_auth_server = f"https://{idp_host}/oauth2"
        jwks_url = f"{okta_auth_server}/v1/keys"
        try:
            jwks_client = jwt.PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=360)
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            data = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": False,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_aud": False,
                    "verify_iss": False,
                },
            )

            return data['groups']
        except:
            pass

        return groups