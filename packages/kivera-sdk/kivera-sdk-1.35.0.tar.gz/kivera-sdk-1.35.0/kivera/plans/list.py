from gql import gql
from typing import Sequence

class listMethods:

    _ListPlansQuery = """
    query ListPlans {
  Plans {
    id
    instance_size
    max_instance_count
    max_total_request_count
    name
    proxy_limit
    min_instance_count
  }
}
    """

    def ListPlans(self):
        query = gql(self._ListPlansQuery)
        variables = {
        }
        operation_name = "ListPlans"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
