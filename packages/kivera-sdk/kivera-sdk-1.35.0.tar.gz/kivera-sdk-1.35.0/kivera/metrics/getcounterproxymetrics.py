from gql import gql
from typing import Sequence

class getcounterproxymetricsMethods:

    _GetCounterProxyMetricsQuery = """
    query GetCounterProxyMetrics {
    Counters_aggregate {
        aggregate {
            sum {
                counter_total_request
                counter_notifies
                counter_denials
                counter_accepts
            }
        }
    }
    Proxies_aggregate(where: {status: {_neq: "DELETED"}}) {
        aggregate {
            count
        }
    }
}
    """

    def GetCounterProxyMetrics(self):
        query = gql(self._GetCounterProxyMetricsQuery)
        variables = {
        }
        operation_name = "GetCounterProxyMetrics"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
