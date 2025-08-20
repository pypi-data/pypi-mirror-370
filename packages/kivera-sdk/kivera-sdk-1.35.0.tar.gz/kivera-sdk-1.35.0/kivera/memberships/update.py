from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateMembershipRoleQuery = """
    mutation UpdateMembershipRole($membership_id: Int!, $role_id: Int!) {
    insert_MembershipRoles_one(object: {
        membership_id: $membership_id,
        role_id: $role_id
    },
    on_conflict: {
        constraint: membershiproles_uniq_key,
        update_columns: role_id
    }) {
        id
        membership_id
        role_id
    }
}
    """

    def UpdateMembershipRole(self, membership_id: int, role_id: int):
        query = gql(self._UpdateMembershipRoleQuery)
        variables = {
            "membership_id": membership_id,
            "role_id": role_id,
        }
        operation_name = "UpdateMembershipRole"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
