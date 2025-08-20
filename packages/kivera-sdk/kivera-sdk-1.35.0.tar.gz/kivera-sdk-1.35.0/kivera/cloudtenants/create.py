from gql import gql
from typing import Sequence

class createMethods:

    _CreateCloudTenantQuery = """
    mutation CreateCloudTenant($organization_id: Int!, $provider_id: Int!, $name: String!, $tenant_structure: jsonb!) {
    insert_CloudTenants_one(
        object: {
            organization_id: $organization_id,
            provider_id: $provider_id,
            name: $name
            tenant_structure: $tenant_structure
        }
    ){
        id
    }
}
    """

    def CreateCloudTenant(self, organization_id: int, provider_id: int, name: str, tenant_structure: dict):
        query = gql(self._CreateCloudTenantQuery)
        variables = {
            "organization_id": organization_id,
            "provider_id": provider_id,
            "name": name,
            "tenant_structure": tenant_structure,
        }
        operation_name = "CreateCloudTenant"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
