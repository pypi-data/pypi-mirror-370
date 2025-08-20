from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteCloudTenantQuery = """
    mutation DeleteCloudTenant($id: Int!) {
    delete_CloudTenants_by_pk(id: $id) {
        id
    }
}
    """

    def DeleteCloudTenant(self, id: int):
        query = gql(self._DeleteCloudTenantQuery)
        variables = {
            "id": id,
        }
        operation_name = "DeleteCloudTenant"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
