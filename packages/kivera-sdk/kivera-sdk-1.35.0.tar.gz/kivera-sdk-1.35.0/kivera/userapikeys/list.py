from gql import gql
from typing import Sequence

class listMethods:

    _ListUserApiKeysQuery = """
    query ListUserApiKeys {
    UserApiKeys {
        client_id
        id
        org_id
        status
        user_id
        created
        description
        Organization {
            domain
            company_name
        }
    }
}
    """

    def ListUserApiKeys(self):
        query = gql(self._ListUserApiKeysQuery)
        variables = {
        }
        operation_name = "ListUserApiKeys"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
