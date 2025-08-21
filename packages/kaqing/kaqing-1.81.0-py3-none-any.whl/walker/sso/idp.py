import getpass
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

from walker.sso import authn_okta
from walker.sso.authenticator import Authenticator
from walker.sso.authn_ad import AdAuthenticator
from walker.sso.sso_config import SsoConfig

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

    def login(app_host: str, username: str = None, forced = False, use_cached = True) -> IdpLogin:
        idp_uri = SsoConfig().find_idp_uri(username, app_host, app_host)

        if use_cached:
            if idp_token := os.getenv('IDP_TOKEN'):
                l0: IdpLogin = IdpLogin.deser(idp_token)
                l1: IdpLogin = Idp.parse_idp_uri(idp_uri)
                if l0.app_login_url == l1.app_login_url:
                    if l0.state != 'EMPTY':
                        return l0

                    l0.state = l1.state

                return l0

        return Idp.with_creds(app_host, idp_uri, forced, username=username)

    def with_creds(app_host: str, idp_uri: str, forced: bool, username: str = None) -> IdpLogin:
        idp = urlparse(idp_uri).hostname

        def resolve_authn():
            if 'okta' in idp.lower():
                return authn_okta.OktaAuthenticator()
            elif 'microsoftonline' in idp.lower():
                return AdAuthenticator()
            else:
                log2(f'{idp} is not supported; only okta and ad are supported.')

                return None

        authn: Authenticator = resolve_authn()
        if not authn:
            return None

        okta = idp.upper().split('.')[0]
        dir = f'{Path.home()}/.kaqing'
        env_f = f'{dir}/.credentials'
        load_dotenv(dotenv_path=env_f)

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

        idp2_uri = SsoConfig().find_idp_uri(username, app_host, app_host)
        if idp != (idp2 := urlparse(idp2_uri).hostname):
            log(f'Switched to {idp2}.')
            idp = idp2
            log(f'{idp} login: {username}')
            authn = resolve_authn()
            idp_uri = idp2_uri

        password = None
        while password == None or Idp.ctrl_c_entered:
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
                r = authn.authenticate(idp_uri, app_host, username, password)

                return r
            finally:
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