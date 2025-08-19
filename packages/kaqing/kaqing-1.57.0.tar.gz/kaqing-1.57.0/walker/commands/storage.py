from walker.commands.command import Command
from walker.commands.commands_utils import show_table
from walker.config import Config
from walker.k8s_utils.statefulsets import StatefulSets
from walker.repl_state import ReplState, RequiredState

class Storage(Command):
    COMMAND = 'storage'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(Storage, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return Storage.COMMAND

    def required(self):
        return RequiredState.CLUSTER_OR_POD

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        args, show_output = Command.extract_options(args, ['-s', '--show'])

        cols = Config().get('storage.columns', 'pod,volume_root,volume_cassandra,snapshots,data,compactions')
        header = Config().get('storage.header', 'POD_NAME,VOLUME /,VOLUME CASS,SNAPSHOTS,DATA,COMPACTIONS')
        if state.pod:
            show_table(state, [state.pod], cols, header, show_output=show_output)
        elif state.sts:
            pod_names = [pod.metadata.name for pod in StatefulSets.pods(state.sts, state.namespace)]
            show_table(state, pod_names, cols, header, show_output=show_output)

        return state

    def completion(self, state: ReplState):
        if not state.sts:
            return {}

        return {Storage.COMMAND: None}

    def help(self, _: ReplState):
        return f'{Storage.COMMAND} [-s]\t show storage overview  -s show commands on nodes'