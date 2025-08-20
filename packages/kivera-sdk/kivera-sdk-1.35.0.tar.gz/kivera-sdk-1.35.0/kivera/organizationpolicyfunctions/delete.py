from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteOrganizationPolicyFunctionQuery = """
    mutation DeleteOrganizationPolicyFunction($org_id: Int!) {
    delete_OrganizationPolicyFunctions(where: {organization_id: {_eq: $org_id}}) {
        affected_rows
    }
}
    """

    def DeleteOrganizationPolicyFunction(self, org_id: int):
        query = gql(self._DeleteOrganizationPolicyFunctionQuery)
        variables = {
            "org_id": org_id,
        }
        operation_name = "DeleteOrganizationPolicyFunction"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
