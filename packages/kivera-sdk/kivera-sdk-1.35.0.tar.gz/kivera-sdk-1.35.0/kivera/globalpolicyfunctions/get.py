from gql import gql
from typing import Sequence

class getMethods:

    _GetGlobalPolicyFunctionQuery = """
    query GetGlobalPolicyFunction($gpfn: String!) {
  GlobalPolicyFunctions(where: {name: {_eq: $gpfn}}) {
    name
    function
    id
  }
}
    """

    def GetGlobalPolicyFunction(self, gpfn: str):
        query = gql(self._GetGlobalPolicyFunctionQuery)
        variables = {
            "gpfn": gpfn,
        }
        operation_name = "GetGlobalPolicyFunction"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
