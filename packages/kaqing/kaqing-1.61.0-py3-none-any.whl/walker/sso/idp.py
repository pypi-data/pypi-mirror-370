import base64
import getpass
import json
import os
from pathlib import Path
import re
from typing import Callable
from dotenv import load_dotenv
import jwt
import jwt.algorithms
import requests
from urllib.parse import urlparse, parse_qs, unquote

from .idp_login import IdpLogin
from walker.config import Config
from walker.k8s_utils.kube_context import KubeContext
from walker.utils import log, log2

class Idp:
    ctrl_c_entered = False

    def __init__(self):
        pass

    def parse_idp_uri(idp_uri: str):
        parsed_url = urlparse(idp_uri)
        query_string = parsed_url.query
        params = parse_qs(query_string)
        state_token = params.get('state', [''])[0]
        redirect_url = params.get('redirect_uri', [''])[0]

        return IdpLogin(app_login_url=redirect_url, id=None, state=state_token)

    def login(app_host: str, idp_uri: str, username: str = None, forced = False, use_cached = True) -> IdpLogin:
        if use_cached:
            if idp_token := os.getenv('IDP_TOKEN'):
                l0: IdpLogin = IdpLogin.deser(idp_token)
                l1: IdpLogin = Idp.parse_idp_uri(idp_uri)
                if l0.app_login_url == l1.app_login_url:
                    if l0.state != 'EMPTY':
                        return l0

                    l0.state = l1.state

                    return l0

        def body(username, password) -> IdpLogin:
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
            if Config().get('debug.show-out', False):
                log2(f'{response.status_code} {url}')
            auth_response = response.json()

            if 'sessionToken' not in auth_response:
                return None

            session_token = auth_response['sessionToken']

            url = f'{idp_uri}&sessionToken={session_token}'
            r = session.get(url)
            if Config().get('debug.show-out', False):
                log2(f'{r.status_code} {url}')

            id_token = Idp.extract(r.text, r'.*name=\"id_token\" value=\"(.*?)\".*')
            if not id_token:
                err = Idp.extract(r.text, r'.*name=\"error_description\" value=\"(.*?)\".*')
                if err:
                    log2(unquote(err).replace('&#x20;', ' '))
                else:
                    log2('id_token not found\n' + r.text)

                return None

            if group := Config().get('app.login.admin-group', '{host}/C3.ClusterAdmin').replace('{host}', app_host):
                if group not in Idp.get_groups(okta_host, id_token):
                    tks = group.split('/')
                    group = tks[len(tks) - 1]
                    log2(f'{username} is not a member of {group}.')

                    return None

            return IdpLogin(redirect_url, id_token, state_token, username, session=session)

        return Idp.with_creds(urlparse(idp_uri).hostname, forced, body, username=username)

    def with_creds(idp: str, forced: bool, body: Callable[[str, str], IdpLogin], username: str = None) -> IdpLogin:
        okta = idp.upper().split('.')[0]
        dir = f'{Path.home()}/.kaqing'
        env_f = f'{dir}/.credentials'
        load_dotenv(dotenv_path=env_f)

        if not 'OKTA' in idp.upper():
            log2(f'{idp} is not supported; only okta.com is supported.')

            return None, None

        # c3energy.okta.com login:
        # Password:
        # username = None
        if username:
            log(f'{idp} login: {username}')

        while not username or Idp.ctrl_c_entered:
            if Idp.ctrl_c_entered:
                Idp.ctrl_c_entered = False

            default_user = os.getenv(f'{okta}_USERNAME')
            if default_user:
                if forced:
                    username = default_user
                else:
                    username = input(f'{idp} login(default {default_user}): ') or default_user
            else:
                username = input(f'{idp} login: ')
        password = None
        while not password or Idp.ctrl_c_entered:
            if Idp.ctrl_c_entered:
                Idp.ctrl_c_entered = False

            default_pass = os.getenv(f'{okta}_PASSWORD')
            if default_pass:
                if forced:
                    password = default_pass
                else:
                    password = getpass.getpass(f'Password(default ********): ') or default_pass
            else:
                password = getpass.getpass(f'Password: ')

        if username and password:
            r: IdpLogin = None
            try:
                r = body(username, password)

                return r
            finally:
                # if r:
                #     self.session = r.session
                if r and Config().get('app.login.cache-creds', True):
                    updated = []
                    if os.path.exists(env_f):
                        with open(env_f, 'r') as file:
                            try:
                                file_content = file.read()
                                for l in file_content.split('\n'):
                                    tks = l.split('=')
                                    key = tks[0]
                                    value = tks[1] if len(tks) > 1 else ''
                                    if key == f'{okta}_USERNAME':
                                        value = username
                                    elif key == f'{okta}_PASSWORD' and not KubeContext.in_cluster():
                                        # do not store password to the .credentials file when in Kubernetes pod
                                        value = password
                                    updated.append(f'{key}={value}')
                            except:
                                updated = None
                                log2('Update failed')
                    else:
                        updated.append(f'{okta}_USERNAME={username}')
                        if not KubeContext.in_cluster():
                            # do not store password to the .credentials file when in Kubernetes pod
                            updated.append(f'{okta}_PASSWORD={password}')

                    if updated:
                        if not os.path.exists(env_f):
                            os.makedirs(dir, exist_ok=True)
                        with open(env_f, "w") as file:
                            file.write('\n'.join(updated))

        return None

    def build_uri(client_id: str, app_host: str):
        # https://c3energy.okta.com/oauth2/v1/authorize?
        # response_type=id_token&
        # response_mode=form_post&
        # client_id=azops88.c3.ai&
        # scope=openid+email+profile+groups&
        # redirect_uri=https%3A%2F%2Fazops88.c3.ai%2Fc3%2Fc3%2Foidc%2Flogin&
        # nonce=9e302354ae1a059d&
        # state=eyJ0eXAiOiJKV1Qi...
        uri = Config().get('idp.uri', 'https://c3energy.okta.com/oauth2/v1/authorize?response_type=id_token&response_mode=form_post&client_id={client_id}&scope=openid+email+profile+groups&redirect_uri=https%3A%2F%2F{host}%2Fc3%2Fc3%2Foidc%2Flogin&state=EMPTY')
        return uri.replace('{client_id}', client_id).replace('{host}', app_host).replace('{nonce}', Idp.generate_oauth_nonce())

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

    def extract(form: str, pattern: re.Pattern):
        value = None

        for l in form.split('\n'):
            # <input type="hidden" name="id_token" value="..."/>
            groups = re.match(pattern, l)
            if groups:
                value = groups[1]

        return value

    def generate_oauth_nonce():
        """Generates a cryptographically secure, base64-encoded nonce."""
        # Generate 32 bytes of cryptographically secure random data
        random_bytes = os.urandom(32)
        # Base64 encode the random bytes
        nonce = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        # Remove any padding characters if desired (e.g., '=' from base64url)
        nonce = nonce.rstrip('=')
        return nonce