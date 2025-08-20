from gql import gql
from typing import Sequence

class getMethods:

    _GetMembershipsQuery = """
    query GetMemberships($user_id: String!) {
    Users(where: {id: {_eq: $user_id }}) {
        id
        active_org_id
        Memberships {
            id
            org_id
        }
    }
}
    """

    def GetMemberships(self, user_id: str):
        query = gql(self._GetMembershipsQuery)
        variables = {
            "user_id": user_id,
        }
        operation_name = "GetMemberships"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
