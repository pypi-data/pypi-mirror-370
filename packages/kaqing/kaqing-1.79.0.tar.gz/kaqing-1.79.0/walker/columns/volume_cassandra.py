from walker.checks.check_result import CheckResult
from walker.checks.disk import Disk
from walker.columns.column import Column
from walker.config import Config

class CassandraVolume(Column):
    def name(self):
        return 'volume_cassandra'

    def checks(self):
        return [Disk()]

    def pod_value(self, check_results: list[CheckResult], pod_name: str):
        # self.init_check_results(check_results)
        r = self.result_by_pod(check_results, pod_name)

        # r = self.r_by_pod[pod_name]
        dd = r.details[Disk().name()]
        cass_data_path = Config().get('checks.cassandra-data-path', '/c3/cassandra')
        cass = dd['devices'][cass_data_path]
        fr = f"{cass['per']}({cass['used']}/{cass['total']})"

        return fr