from gql import gql
from typing import Sequence

class createMethods:

    _CreateMembershipQuery = """
    mutation CreateMembership($user_id: String!, $org_id: Int!) {
    insert_Memberships_one(object: {user_id: $user_id, org_id: $org_id}) {
        id
        user_id
        org_id
    }
}
    """

    def CreateMembership(self, user_id: str, org_id: int):
        query = gql(self._CreateMembershipQuery)
        variables = {
            "user_id": user_id,
            "org_id": org_id,
        }
        operation_name = "CreateMembership"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
