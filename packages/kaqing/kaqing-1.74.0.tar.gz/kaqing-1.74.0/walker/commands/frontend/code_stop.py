import subprocess

from walker.commands.command import Command
from walker.k8s_utils.ingresses import Ingresses
from walker.k8s_utils.services import Services
from walker.repl_state import ReplState, RequiredState
from walker.utils import log2

class CodeStop(Command):
    COMMAND = 'code stop'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(CodeStop, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return CodeStop.COMMAND

    def required(self):
        return RequiredState.NAMESPACE

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        if not args:
            log2('Please specify <port>.')
            return state

        port = args[0]
        name = f'ops-{port}'
        Ingresses.delete_ingress(name, state.namespace)
        Services.delete_service(name, state.namespace)

        pattern = f'/c3/c3/ops-code/{port}/'
        self.kill_process_by_pattern(pattern)

        return state

    def completion(self, state: ReplState):
        if state.namespace:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{CodeStop.COMMAND}\t stop code server'

    def kill_process_by_pattern(self, pattern):
        """
        Finds and kills processes matching a given pattern.
        """
        try:
            # Find PIDs of processes matching the pattern, excluding the grep process itself
            command = f"ps aux | grep '{pattern}' | grep -v 'grep' | awk '{{print $2}}'"
            process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            pids = process.stdout.strip().split('\n')

            if not pids or pids == ['']:
                print(f"No processes found matching pattern: '{pattern}'")
                return

            for pid in pids:
                if pid:  # Ensure PID is not empty
                    try:
                        subprocess.run(f"kill -9 {pid}", shell=True, check=True)
                        print(f"Killed process with PID: {pid} (matching pattern: '{pattern}')")
                    except subprocess.CalledProcessError as e:
                        print(f"Error killing process {pid}: {e}")

        except subprocess.CalledProcessError as e:
            print(f"Error finding processes: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")