import os
from pathlib import Path
import socket

from walker.apps import Apps
from walker.commands.command import Command
from walker.k8s_utils.ingresses import Ingresses
from walker.k8s_utils.services import Services
from walker.repl_state import ReplState, RequiredState
from walker.utils import log2, random_alphanumeric

class CodeStart(Command):
    COMMAND = 'code start'

    # the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'): cls.instance = super(CodeStart, cls).__new__(cls)

        return cls.instance

    def __init__(self, successor: Command=None):
        super().__init__(successor)

    def command(self):
        return CodeStart.COMMAND

    def required(self):
        return RequiredState.NAMESPACE

    def run(self, cmd: str, state: ReplState):
        if not(args := self.args(cmd)):
            return super().run(cmd, state)

        state, args = self.apply_state(args, state)
        if not self.validate_state(state):
            return state

        log2('This will support c3/c3 only for demo.')

        try:
            id = random_alphanumeric(8)
            port = self.get_available_port()
            name = f'ops-{port}'
            base_path = f'/c3/c3/ops/code/{port}/{id}'
            host = Apps.app_host('c3', 'c3', state.namespace)
            Services.create_service(name, state.namespace, port, {"run": "ops"}, labels={
                'user': os.getenv('USER')
            })
            Ingresses.create_ingress(name, state.namespace, host, f'{base_path}/(.*)', port, annotations={
                'kubernetes.io/ingress.class': 'nginx',
                'nginx.ingress.kubernetes.io/use-regex': 'true',
                'nginx.ingress.kubernetes.io/rewrite-target': '/$1'
            }, labels={
                'user': os.getenv('USER')
            }, path_type='Prefix')
            # code-server --auth none --abs-proxy-base-path base_path $HOME
            code_cmd = f'code-server --auth none --bind-addr 0.0.0.0:{port} --abs-proxy-base-path {base_path} {Path.home()}'
            log2(code_cmd)
            log2(f'* vscode is available at https://{host}{base_path}/ *')
            os.system(code_cmd)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            if e.status == 409:
                log2(f"Error: '{name}' already exists in namespace '{state.namespace}'.")
            else:
                log2(f"Error creating ingress or service: {e}")

        return state

    def completion(self, state: ReplState):
        if state.namespace:
            return super().completion(state)

        return {}

    def help(self, _: ReplState):
        return f'{CodeStart.COMMAND}\t start code server'

    def get_available_port(self):
        """
        Finds and returns an available local port.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', 0))  # Bind to localhost and let OS assign a free port
            return s.getsockname()[1]  # Return the assigned port number