from walker.checks.check_result import CheckResult
from walker.checks.status import Status
from walker.columns.column import Column

class NodeTokens(Column):
    def name(self):
        return 'tokens'

    def checks(self):
        return [Status()]

    def host_value(self, _: list[CheckResult], status: dict[str, any]):
        return status[self.name()]