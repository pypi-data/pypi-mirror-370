from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateCloudTenantQuery = """
    mutation UpdateCloudTenant($id: Int!, $name: String!, $tenant_structure: jsonb!) {
    update_CloudTenants_by_pk(pk_columns: { id: $id}, _set: { name: $name, tenant_structure: $tenant_structure}) {
        id
        name
        tenant_structure
        Provider {
            id
            name
        }
    }
}
    """

    def UpdateCloudTenant(self, id: int, name: str, tenant_structure: dict):
        query = gql(self._UpdateCloudTenantQuery)
        variables = {
            "id": id,
            "name": name,
            "tenant_structure": tenant_structure,
        }
        operation_name = "UpdateCloudTenant"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
