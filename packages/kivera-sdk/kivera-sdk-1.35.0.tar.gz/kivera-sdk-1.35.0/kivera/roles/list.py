from gql import gql
from typing import Sequence

class listMethods:

    _ListRolesQuery = """
    query ListRoles {
    Roles {
        id
        role_name
    }
}
    """

    def ListRoles(self):
        query = gql(self._ListRolesQuery)
        variables = {
        }
        operation_name = "ListRoles"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
