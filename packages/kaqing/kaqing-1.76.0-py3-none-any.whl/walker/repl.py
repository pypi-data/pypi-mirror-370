import re
import time
import traceback
import click
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.key_binding import KeyBindings

from walker.cli_group import cli
from walker.commands.command import Command
from walker.commands.command_helpers import ClusterCommandHelper
from walker.commands.help import Help
from walker.commands.postgres.postgres_session import PostgresSession
from walker.config import Config
from walker.k8s_utils.kube_context import KubeContext
from walker.k8s_utils.statefulsets import StatefulSets
from walker.repl_commands import ReplCommands
from walker.repl_session import ReplSession
from walker.repl_state import ReplState
from walker.utils import deep_merge_dicts, lines_to_tabular, log2
from walker.apps import Apps
from . import __version__

def enter_repl(state: ReplState):
    cmd_list = ReplCommands.repl_cmd_list() + [Help()]
    # head with the Chain of Responsibility pattern
    cmds: Command = Command.chain(cmd_list)
    session = ReplSession().prompt_session

    def prompt_msg():
        msg = ''
        if state.device == ReplState.P:
            msg = f'{ReplState.P}:'
            pg = PostgresSession(state.namespace, state.pg_path) if state.pg_path else None
            if pg and pg.db:
                msg += pg.db
            elif pg and pg.host:
                msg += pg.host
        elif state.device == ReplState.A:
            msg = f'{ReplState.A}:'
            if state.app_env:
                msg += state.app_env
            if state.app_app:
                msg += f'/{state.app_app}'
        else:
            msg = f'{ReplState.C}:'
            if state.pod:
                # cs-d0767a536f-cs-d0767a536f-default-sts-0
                group = re.match(r".*?-.*?-(.*)", state.pod)
                msg += group[1]
            elif state.sts:
                # cs-d0767a536f-cs-d0767a536f-default-sts
                group = re.match(r".*?-.*?-(.*)", state.sts)
                msg += group[1]

        return f"{msg}$ " if state.bash_session else f"{msg}> "

    log2(f'kaqing {__version__}')
    ss = StatefulSets.list_sts_name_and_ns()

    if state.device == ReplState.C:
        if not ss:
            raise Exception("no Cassandra clusters found")
        elif len(ss) == 1 and Config().get('repl.auto-enter-only-cluster', True):
            cluster = ss[0]
            state.sts = cluster[0]
            state.namespace = cluster[1]
            state.wait_log(f'Moving to the only Cassandra cluster: {state.sts}@{state.namespace}...')
    elif state.device == ReplState.A:
        if app := Config().get('repl.auto-enter-app', 'c3/c3'):
            if app != 'no':
                ea = app.split('/')
                state.app_env = ea[0]
                if len(ea) > 1:
                    state.app_app = ea[1]
                    state.wait_log(f'Moving to {state.app_env}/{state.app_app}...')
                else:
                    state.wait_log(f'Moving to {state.app_env}...')

    kb = KeyBindings()

    @kb.add('c-c')
    def _(event):
        event.app.current_buffer.text = ''

    while True:
        try:
            completer = NestedCompleter.from_nested_dict({})
            if not state.bash_session:
                completions = {}
                if state.app_app:
                    completions = Apps(path='apps.yaml').commands()
                    # completions = {k: None for k in Apps(path='apps.yaml').commands()}

                for cmd in cmd_list:
                    s1 = time.time()
                    try:
                        completions = deep_merge_dicts(completions, cmd.completion(state))
                    finally:
                        if Config().get('debug.timings', False):
                            print('Timing completion calc', cmd.command(), f'{time.time() - s1:.2f}')
                        pass

                completer = NestedCompleter.from_nested_dict(completions)

            cmd = session.prompt(prompt_msg(), completer=completer, key_bindings=kb)
            s0 = time.time()

            if state.bash_session:
                if cmd.strip(' ') == 'exit':
                    state.exit_bash()
                    continue

                cmd = f'bash {cmd}'

            if cmd and cmd.strip(' ') and not cmds.run(cmd, state):
                c_sql_tried = False
                if state.device == ReplState.P:
                    pg = PostgresSession(state.namespace, state.pg_path)
                    if pg.db:
                        c_sql_tried = True
                        cmd = f'pg {cmd}'
                        cmds.run(cmd, state)
                elif state.device == ReplState.A:
                    if state.app_app:
                        c_sql_tried = True
                        cmd = f'app {cmd}'
                        cmds.run(cmd, state)
                elif state.sts:
                    c_sql_tried = True
                    cmd = f'cql {cmd}'
                    cmds.run(cmd, state)

                if not c_sql_tried:
                    log2(f'* Invalid command: {cmd}')
                    log2()
                    lines = [c.help(state) for c in cmd_list if c.help(state)]
                    log2(lines_to_tabular(lines, separator='\t'))
        except EOFError:  # Handle Ctrl+D (EOF) for graceful exit
            break
        except Exception as e:
            if Config().get('debug.exit-on-error', False):
                raise e
            else:
                # log2(e)
                traceback.print_exc()
        finally:
            state.clear_wait_log_flag()
            if Config().get('debug.timings', False) and 'cmd' in locals() and 's0' in locals():
                print('Timing command', cmd, f'{time.time() - s0:.2f}')

@cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True), cls=ClusterCommandHelper, help="Enter interactive shell.")
@click.option('--kubeconfig', '-k', required=False, metavar='path', help='path to kubeconfig file')
@click.option('--config', default='params.yaml', metavar='path', help='path to kaqing parameters file')
@click.option('--param', '-v', multiple=True, metavar='<key>=<value>', help='parameter override')
@click.option('--cluster', '-c', required=False, metavar='statefulset', help='Kubernetes statefulset name')
@click.option('--namespace', '-n', required=False, metavar='namespace', help='Kubernetes namespace')
@click.argument('extra_args', nargs=-1, metavar='[cluster]', type=click.UNPROCESSED)
def repl(kubeconfig: str, config: str, param: list[str], cluster:str, namespace: str, extra_args):
    KubeContext.init_config(kubeconfig)
    if not KubeContext.init_params(config, param):
        return

    state = ReplState(device=Config().get('repl.start-drive', 'a'), ns_sts=cluster, namespace=namespace, in_repl=True)
    state, _ = state.apply_args(extra_args)
    enter_repl(state)