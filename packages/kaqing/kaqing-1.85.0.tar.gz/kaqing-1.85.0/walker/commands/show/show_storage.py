from walker.commands.storage import Storage
from walker.commands.command import Command
from walker.repl_state import ReplState

class ShowStorage(Command):
    COMMAND = 'show storage'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowStorage, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowStorage.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        Storage().run(Storage.COMMAND, state)

        return state

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ShowStorage.COMMAND} [-s]\t show storage overview  -s show commands on nodes'