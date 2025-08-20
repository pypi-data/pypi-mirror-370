from gql import gql
from typing import Sequence

class listMethods:

    _ListGlobalPolicyFunctionsQuery = """
    query ListGlobalPolicyFunctions {
    GlobalPolicyFunctions(order_by: {id: asc}) {
    id
    name
    function
    }
}
    """

    def ListGlobalPolicyFunctions(self):
        query = gql(self._ListGlobalPolicyFunctionsQuery)
        variables = {
        }
        operation_name = "ListGlobalPolicyFunctions"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
