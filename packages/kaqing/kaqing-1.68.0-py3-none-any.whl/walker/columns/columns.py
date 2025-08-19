from walker.columns.column import Column
from walker.columns.compactions import Compactions
from walker.columns.cpu import Cpu
from walker.columns.dir_data import DataDir
from walker.columns.dir_snapshots import SnapshotsDir
from walker.columns.gossip import Gossip
from walker.columns.host_id import HostId
from walker.columns.memory import Memory
from walker.columns.node_address import NodeAddress
from walker.columns.node_load import NodeLoad
from walker.columns.node_owns import NodeOwns
from walker.columns.node_status import NodeStatus
from walker.columns.node_tokens import NodeTokens
from walker.columns.pod_name import PodName
from walker.columns.volume_cassandra import CassandraVolume
from walker.columns.volume_root import RootVolume

def collect_checks(columns: list[Column]):
    checks = sum([c.checks() for c in columns], [])
    return {cc.name(): cc for cc in checks}.values()

class Columns:
    COLUMNS_BY_NAME = None

    def all_columns():
        return [Compactions(), Cpu(), DataDir(), SnapshotsDir(), Gossip(), HostId(), Memory(),
                NodeAddress(), NodeLoad(), NodeOwns(), NodeStatus(),NodeTokens(), PodName(), CassandraVolume(), RootVolume()]

    def columns_by_name():
        return {c.name(): c.__class__ for c in Columns.all_columns()}

    def create_columns(columns: str):
        if not Columns.COLUMNS_BY_NAME:
            Columns.COLUMNS_BY_NAME = Columns.columns_by_name()

        cols = []
        for name in columns.split(','):
            name = name.strip(' ')
            if not name in Columns.COLUMNS_BY_NAME:
                return None
            cols.append(Columns.COLUMNS_BY_NAME[name]())

        return cols
