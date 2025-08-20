from gql import gql
from typing import Sequence

class listMethods:

    _ListCloudTenantsQuery = """
    query ListCloudTenants {
    CloudTenants {
        id
        name
        organization_id
        created_at
        updated_at
        UpdatedByUser {
            family_name
            given_name
            id
        }
        CreatedByUser {
            family_name
            id
            given_name
        }
        Provider {
            id
            name
        }
    }
}
    """

    def ListCloudTenants(self):
        query = gql(self._ListCloudTenantsQuery)
        variables = {
        }
        operation_name = "ListCloudTenants"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
