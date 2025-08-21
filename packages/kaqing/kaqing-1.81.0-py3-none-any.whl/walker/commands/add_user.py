import signal
import traceback

from walker.app_session import AppSession
from walker.apps import Apps
from walker.sso.idp import Idp
from walker.sso.idp_login import IdpLogin
from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.utils import log, log2

class AddAdmin(Command):
    COMMAND = 'add admin'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(AddAdmin, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return AddAdmin.COMMAND

    def run(self, cmd: str, state: ReplState):
        def custom_handler(signum, frame):
            AppSession.ctrl_c_entered = True

        signal.signal(signal.SIGINT, custom_handler)

        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

        args, print_token = Command.extract_options(args, '--print-token')

        username: str = None
        if len(args) > 0:
            username = args[0]

        login: IdpLogin = None
        while not login:
            try:
                if not(host := Apps.app_host('c3', 'c3', state.namespace)):
                    log2('Cannot locate ingress for app.')
                    username = None
                    continue

                if not (login := Idp.login(host, username=username, use_cached=False)):
                    log2('Invalid username/password. Please try again.')
                    username = None
            except:
                log2(traceback.format_exc())
                pass

        if print_token:
            log(f'IDP_TOKEN={login.ser()}')

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{AddAdmin.COMMAND}\t SSO login'