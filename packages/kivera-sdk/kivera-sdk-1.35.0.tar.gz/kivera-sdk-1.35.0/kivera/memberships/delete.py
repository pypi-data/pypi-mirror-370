from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteMembershipQuery = """
    mutation DeleteMembership($membership_id: Int!){
    delete_MembershipRoles(where: {membership_id: {_eq: $membership_id}}) {
        affected_rows
    }
    delete_Memberships(where: {id: {_eq: $membership_id}}) {
        affected_rows
        returning {
            user_id
            org_id
        }
    }
}
    """

    def DeleteMembership(self, membership_id: int):
        query = gql(self._DeleteMembershipQuery)
        variables = {
            "membership_id": membership_id,
        }
        operation_name = "DeleteMembership"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
