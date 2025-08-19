import sys
import os

from walker.utils import log2

current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(current_dir))

parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.append(grandparent_dir)

from version import __version__
from walker.commands.command import Command
from walker.repl_state import ReplState

class ShowVersion(Command):
    COMMAND = 'show version'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(ShowVersion, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return ShowVersion.COMMAND

    def run(self, cmd: str, state: ReplState):
        if not self.args(cmd):
            return super().run(cmd, state)

        log2(__version__)

        return state

    def completion(self, state: ReplState):
        return super().completion(state)

    def help(self, _: ReplState):
        return f'{ShowVersion.COMMAND}\t show kaqing version'