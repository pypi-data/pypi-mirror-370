import click

from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper
from .show_params import ShowParams
from .show_app_id import ShowAppId
from .show_cassandra_status import ShowCassandraStatus
from .show_cassandra_version import ShowCassandraVersion
from .show_commands import ShowKubectlCommands
from .show_processes import ShowProcesses
from .show_repairs import ShowRepairs
from .show_storage import ShowStorage
from .show_version import ShowVersion
from walker.repl_state import ReplState, RequiredState
from walker.utils import lines_to_tabular, log, log2

class Show(Command):
    COMMAND = 'show'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Show, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Show.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if state.in_repl and not self.validate_state(state):
            return state

        if state.in_repl:
            log(lines_to_tabular([c.help(ReplState()) for c in Show.cmd_list()], separator=':'))

            return 'command-missing'
        else:
            # head with the Chain of Responsibility pattern
            cmds = Command.chain(Show.cmd_list())
            if not cmds.run(cmd, state):
                log2('* Command is missing.')
                Command.display_help()

    def cmd_list():
        return [ShowKubectlCommands(), ShowParams(), ShowProcesses(), ShowRepairs(), ShowStorage(), ShowVersion(),
                ShowCassandraStatus(), ShowCassandraVersion()]

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f"{Show.COMMAND}\t show kubectl commands"

class ShowCommandHelper(click.Command):
    def get_help(self, ctx: click.Context):
        log(super().get_help(ctx))
        log()
        log('Catogories:')

        log(lines_to_tabular([c.help(ReplState()).replace(f'{Show.COMMAND} ', '  ', 1) for c in Show.cmd_list()], separator=':'))
        log()
        ClusterCommandHelper.cluster_help()