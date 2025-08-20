from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateOrganizationPolicyFunctionV2Query = """
    mutation UpdateOrganizationPolicyFunctionV2($org_id: Int!, $function: String!) {
    insert_OrganizationPolicyFunctions_one(object: {organization_id: $org_id, function: $function}, on_conflict: {constraint: organizationpolicyfunctions_uniq_key, update_columns: function}) {
        organization_id
        id
        function
    }
}
    """

    def UpdateOrganizationPolicyFunctionV2(self, org_id: int, function: str):
        query = gql(self._UpdateOrganizationPolicyFunctionV2Query)
        variables = {
            "org_id": org_id,
            "function": function,
        }
        operation_name = "UpdateOrganizationPolicyFunctionV2"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
