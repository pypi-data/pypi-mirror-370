from gql import gql
from typing import Sequence

class createMethods:

    _CreateAndUpdateOrganizationPolicyFunctionQuery = """
    mutation CreateAndUpdateOrganizationPolicyFunction($org_id: Int!, $function: String!, $name: String) {
    insert_OrganizationPolicyFunctions_one(object: {organization_id: $org_id, function: $function, name: $name}, on_conflict: {constraint: organizationpolicyfunctions_uniq_key, update_columns: function}) {
        organization_id
        id
        function
    }
}
    """

    def CreateAndUpdateOrganizationPolicyFunction(self, org_id: int, function: str, name: str = None):
        query = gql(self._CreateAndUpdateOrganizationPolicyFunctionQuery)
        variables = {
            "org_id": org_id,
            "function": function,
            "name": name,
        }
        operation_name = "CreateAndUpdateOrganizationPolicyFunction"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _CreateOrganizationPolicyFunctionV2Query = """
    mutation CreateOrganizationPolicyFunctionV2($organization_id: Int!, $function: String!) {
    insert_OrganizationPolicyFunctions_one(object: {organization_id: $organization_id, function: $function}, on_conflict: {constraint: organizationpolicyfunctions_uniq_key, update_columns: function}) {
        organization_id
        id
        function
    }
}
    """

    def CreateOrganizationPolicyFunctionV2(self, organization_id: int, function: str):
        query = gql(self._CreateOrganizationPolicyFunctionV2Query)
        variables = {
            "organization_id": organization_id,
            "function": function,
        }
        operation_name = "CreateOrganizationPolicyFunctionV2"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
