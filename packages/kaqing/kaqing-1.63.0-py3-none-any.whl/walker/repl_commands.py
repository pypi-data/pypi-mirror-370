from walker.commands.app import App
from walker.commands.app_ping import AppPing
from walker.commands.show.show_app_queues import ShowAppQueues
from walker.commands.cp import ClipboardCopy
from walker.commands.bash import Bash
from walker.commands.cd import Cd
from walker.commands.check import Check
from walker.commands.command import Command
from walker.commands.cqlsh import Cqlsh
from walker.commands.devices import DeviceApp, DeviceCass, DevicePostgres
from walker.commands.exit import Exit
from walker.commands.medusa.medusa import Medusa
from walker.commands.param_get import GetParam
from walker.commands.issues import Issues
from walker.commands.ls import Ls
from walker.commands.nodetool import NodeTool
from walker.commands.postgres.postgres import Postgres
from walker.commands.preview_table import PreviewTable
from walker.commands.processes import Processes
from walker.commands.pwd import Pwd
from walker.commands.reaper.reaper import Reaper
from walker.commands.repair.repair import Repair
from walker.commands.report import Report
from walker.commands.restart import Restart
from walker.commands.rollout import RollOut
from walker.commands.param_set import SetParam
from walker.commands.show.show import Show
from walker.commands.show.show_app_actions import ShowAppActions
from walker.commands.show.show_app_id import ShowAppId
from walker.commands.status import Status
from walker.commands.storage import Storage
from walker.commands.watch import Watch

class ReplCommands:
    def repl_cmd_list() -> list[Command]:
        return ReplCommands.app() + [DeviceApp(), DevicePostgres(), DeviceCass()] + ReplCommands.navigation() + \
               ReplCommands.cassandra_check() + ReplCommands.cassandra_ops() + ReplCommands.tools() + ReplCommands.exit()

    def navigation() -> list[Command]:
        return [Ls(), PreviewTable(), Cd(), Pwd(), ClipboardCopy(), GetParam(), SetParam()] + Show.cmd_list()

    def cassandra_check() -> list[Command]:
        return [Check(), Issues(), NodeTool(), Processes(), Report(), Status(), Storage()]

    def cassandra_ops() -> list[Command]:
        return Medusa.cmd_list() + [Restart(), RollOut(), Watch()] + Reaper.cmd_list() + Repair.cmd_list()

    def tools() -> list[Command]:
        return [Cqlsh(), Postgres(), Bash()]

    def app() -> list[Command]:
        return [ShowAppActions(), ShowAppId(), ShowAppQueues(), AppPing(), App(), ]
        # return [C3Echo(), C3IqCount(), C3()]

    def exit() -> list[Command]:
        return [Exit()]