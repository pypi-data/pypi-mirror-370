from gql import gql
from typing import Sequence

class getMethods:

    _GetCountersAggregateQuery = """
    query GetCountersAggregate {
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

    def GetCountersAggregate(self):
        query = gql(self._GetCountersAggregateQuery)
        variables = {
        }
        operation_name = "GetCountersAggregate"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
