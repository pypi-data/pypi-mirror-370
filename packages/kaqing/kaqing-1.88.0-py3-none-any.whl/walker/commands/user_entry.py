import os
import signal
import traceback

from walker.sso.idp import Idp
from walker.app_session import AppSession, IdpLogin
from walker.apps import Apps
from walker.commands.command import Command
from walker.repl_state import ReplState
from walker.utils import log2

class UserEntry(Command):
    COMMAND = 'entry'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(UserEntry, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return UserEntry.COMMAND

    def run(self, cmd: str, state: ReplState):
        def custom_handler(signum, frame):
            AppSession.ctrl_c_entered = True

        signal.signal(signal.SIGINT, custom_handler)

        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)

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
                # log2(traceback.format_exc())
                pass

        sh = f'{os.getcwd()}/login.sh'
        if not os.path.exists(sh):
            sh = f'{os.getcwd()}/docker/login.sh'

        os.system(f'{sh} {login.shell_user()} {login.ser()}')

        return state

    def completion(self, _: ReplState):
        return {}

    def help(self, _: ReplState):
        return f'{UserEntry.COMMAND}\t ttyd user entry'