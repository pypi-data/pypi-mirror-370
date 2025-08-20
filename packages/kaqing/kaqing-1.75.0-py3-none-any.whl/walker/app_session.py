import threading
import time
import requests
from urllib.parse import urlparse

from walker.sso.idp import Idp
from walker.sso.idp_login import IdpLogin
from walker.config import Config
from walker.k8s_utils.custom_resources import CustomResources
from walker.k8s_utils.ingresses import Ingresses
from walker.utils import json_to_csv, lines_to_tabular, log, log2
from walker.apps import Apps

class AppSession:
    sessions_by_sts = {}
    sessions_by_host = {}

    def __init__(self, host: str = None, env: str = None):
        self.host = host
        self.env = env
        self.session: requests.Session = None
        self.session: requests.Session = None

    def create_for_sts(sts: str, namespace: str) -> 'AppSession':
        key = f'{sts}@{namespace}'
        if key in AppSession.sessions_by_sts:
            return AppSession.sessions_by_sts[key]

        app_id = CustomResources.get_app_id(sts, namespace)
        if not app_id:
            log2('Cannot locate app custom resource.')

            return None

        h3 = app_id.split('-')
        ingress_name = Config().get('app.login.ingress', '{app_id}-k8singr-appleader-001').replace('{app_id}', app_id)
        host = f"{Ingresses.get_host(ingress_name, namespace)}/{h3[1]}/{h3[2]}"
        if not host:
            log2('Cannot locate ingress for app.')

            return None

        session = AppSession(host)

        AppSession.sessions_by_sts[key] = session

        return session

    def create(env: str, app: str, namespace: str = None) -> 'AppSession':
        if not(host := Apps.app_host(env, app, namespace)):
            log2('Cannot locate ingress for app.')

            return None

        key = f'{host}/{env}'
        if key in AppSession.sessions_by_host:
            return AppSession.sessions_by_host[key]

        session = AppSession(host, env)

        AppSession.sessions_by_host[key] = session

        return session

    def run(env: str, app: str, namespace: str, type: str, action: str, payload: any = None, forced = False):
        app_session: AppSession = AppSession.create(env, app, namespace)

        def run0(session: requests.Session, retried: bool):
            if session:
                with session as session:
                    uri = f'https://{app_session.host}/{env}/{app}/api/8/{type}/{action}'
                    r = session.post(uri, json=payload, headers={
                        'X-Request-Envelope': 'true'
                    })

                    if Config().get('debug.show-out', False):
                        log2(f'{r.status_code} {uri}')
                        log2(payload)

                    if r.status_code >= 200 and r.status_code < 300 or r.status_code == 400:
                        try:
                            js = r.json()
                            try:
                                header, lines = json_to_csv(js, delimiter='\t')
                                log(lines_to_tabular(lines, header=header, separator='\t'))
                            except:
                                log(js)
                        except:
                            if urlparse(r.url).hostname != urlparse(uri).hostname and not retried:
                                session, _ = app_session.login(forced=forced, use_cached=False)
                                retried = True

                                return run0(session, True)

                            if r.text:
                                log2(f'{r.status_code} {r.url} Failed parsing the results.')
                                if Config().get('debug.show-out', False):
                                    log2(r.text)
                    else:
                        log2(r.status_code)
                        log2(r.text)

        session, _ = app_session.login(forced=forced)
        run0(session, False)

    def login(self, forced = False, use_cached=True) -> tuple[requests.Session, str]:
        if not forced and self.session:
            return self.session, None

        idp_login: IdpLogin = Idp.login(self.host, self.idp_redirect_url(), forced=forced, use_cached=use_cached)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        form_data = {
            'state': idp_login.state,
            'id_token': idp_login.id
        }

        stop_event = threading.Event()

        session = idp_login.session
        if not session:
            session = requests.Session()

        def login():
            try:
                timeout = Config().get('app.login.timeout', 5)
                if Config().get('debug.show-out', False):
                    log2(f'-> {idp_login.app_login_url}')
                session.post(idp_login.app_login_url, headers=headers, data=form_data, timeout=timeout)
            except Exception:
                pass
            finally:
                stop_event.set()

        my_thread = threading.Thread(target=login, daemon=True)
        my_thread.start()

        app_access_token = None
        while not app_access_token and not stop_event.is_set():
            time.sleep(1)

            try:
                check_uri = Config().get('app.login.session-check-url', 'https://{host}/{env}/{app}/api/8/C3/userSessionToken').replace('{host}', self.host).replace('{env}', self.env).replace('{app}', 'c3')
                r = session.get(check_uri)
                if Config().get('debug.show-out', False):
                    log2(f'{r.status_code} {check_uri}')

                app_access_token = r.json()['signedToken']
            except Exception:
                pass

        return session, app_access_token

    def idp_redirect_url(self, show_endpoints = True) -> str:
        # stgawsscpsr-c3-c3
        uri = Config().get('app.login.url', 'https://{host}/{env}/{app}').replace('{host}', self.host).replace('{env}', self.env).replace('{app}', 'c3')
        r = requests.get(uri)

        parsed_url = urlparse(r.url)
        if show_endpoints:
            log2(f'{r.status_code} {uri} <-> {parsed_url.hostname}...')
        if r.status_code < 200 or r.status_code > 299:
            return None

        return r.url