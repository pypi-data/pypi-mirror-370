from gql import gql
from typing import Sequence

class getMethods:

    _GetCloudTenantQuery = """
    query GetCloudTenant($id: Int!) {
    CloudTenants_by_pk(id: $id) {
        id
        name
        organization_id
        Provider {
            id
            name
        }
        tenant_structure
    }
}
    """

    def GetCloudTenant(self, id: int):
        query = gql(self._GetCloudTenantQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetCloudTenant"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetCloudTenantsQuery = """
    query GetCloudTenants {
    CloudTenants {
        id
        name
        organization_id
        Provider {
            id
            name
        }
        tenant_structure
    }
}
    """

    def GetCloudTenants(self):
        query = gql(self._GetCloudTenantsQuery)
        variables = {
        }
        operation_name = "GetCloudTenants"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
