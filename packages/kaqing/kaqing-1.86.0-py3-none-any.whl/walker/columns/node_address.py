from walker.checks.check_result import CheckResult
from walker.checks.status import Status
from walker.columns.column import Column

class NodeAddress(Column):
    def name(self):
        return 'address'

    def checks(self):
        return [Status()]

    def host_value(self, _: list[CheckResult], status: dict[str, any]):
        return status[self.name()]