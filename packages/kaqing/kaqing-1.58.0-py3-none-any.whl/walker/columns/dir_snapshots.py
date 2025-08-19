from walker.checks.check_result import CheckResult
from walker.checks.disk import Disk
from walker.columns.column import Column

class SnapshotsDir(Column):
    def name(self):
        return 'snapshots'

    def checks(self):
        return [Disk()]

    def pod_value(self, check_results: list[CheckResult], pod_name: str):
        r = self.result_by_pod(check_results, pod_name)

        dd = r.details[Disk().name()]

        return f"{dd['snapshot']}G"