from gql import gql
from typing import Sequence

class listMethods:

    _ListOrgMembershipsQuery = """
    query ListOrgMemberships($org_id: Int!) {
  Memberships(where: {org_id: {_eq: $org_id}}) {
    id
    org_id
    MembershipRoles {
        Role {
            role_name
            id
        }
    }
    User {
        id
        email
        given_name
        family_name
        verified
        active_org_id
        country_iso_code
        created_at
        id
    }
  }
}
    """

    def ListOrgMemberships(self, org_id: int):
        query = gql(self._ListOrgMembershipsQuery)
        variables = {
            "org_id": org_id,
        }
        operation_name = "ListOrgMemberships"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _ListUserMembershipsQuery = """
    query ListUserMemberships($user_id: String!) {
  Memberships(where: {user_id: {_eq: $user_id}}) {
    id
    MembershipRoles {
        Role {
            role_name
            id
        }
    }
    Organization {
        id
        company_name
    }
  }
}
    """

    def ListUserMemberships(self, user_id: str):
        query = gql(self._ListUserMembershipsQuery)
        variables = {
            "user_id": user_id,
        }
        operation_name = "ListUserMemberships"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
