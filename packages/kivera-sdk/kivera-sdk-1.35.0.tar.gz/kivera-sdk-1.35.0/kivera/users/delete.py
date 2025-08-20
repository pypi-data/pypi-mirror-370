from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteUserFromOrganizationQuery = """
    mutation DeleteUserFromOrganization($org_id: Int!, $user_id: String!) {
    delete_MembershipRoles(where: {Membership: {org_id: {_eq: $org_id}, user_id: {_eq: $user_id}}}) {
        returning {
            id
            membership_id
            role_id
        }
    }
    delete_Memberships(where: {org_id: {_eq: $org_id}, user_id: {_eq: $user_id}}) {
        returning {
            id
            org_id
            review_weekly_summary
            user_id
        }
    }
}
    """

    def DeleteUserFromOrganization(self, org_id: int, user_id: str):
        query = gql(self._DeleteUserFromOrganizationQuery)
        variables = {
            "org_id": org_id,
            "user_id": user_id,
        }
        operation_name = "DeleteUserFromOrganization"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
