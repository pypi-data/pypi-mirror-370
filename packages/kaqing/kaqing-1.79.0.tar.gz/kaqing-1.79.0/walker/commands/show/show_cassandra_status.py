from walker.commands.status import Status
from walker.commands.command import Command
from walker.repl_state import ReplState

class ShowCassandraStatus(Command):
    COMMAND = 'show cassandra status'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowCassandraStatus, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowCassandraStatus.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        Status().run(Status.COMMAND, state)

        return state

    def completion(self, state: ReplState):
        if state.sts:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{ShowCassandraStatus.COMMAND} [-s]\t show merged nodetool status  -s show commands on nodes'