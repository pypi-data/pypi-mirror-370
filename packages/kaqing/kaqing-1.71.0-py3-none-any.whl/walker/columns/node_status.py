from walker.checks.check_result import CheckResult
from walker.checks.status import Status
from walker.columns.column import Column

class NodeStatus(Column):
    def name(self):
        return 'status'

    def checks(self):
        return [Status()]

    def host_value(self, _: list[CheckResult], status: dict[str, any]):
        return status[self.name()]