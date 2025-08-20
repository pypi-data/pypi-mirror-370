from gql import gql
from typing import Sequence

class listMethods:

    _ListUsersQuery = """
    query ListUsers {
  Users {
    id
    verified
    email
    given_name
    family_name
    created_at
    Memberships {
      id
      MembershipRoles {
        Role {
          role_name
          id
        }
      }
    }
  }
}
    """

    def ListUsers(self):
        query = gql(self._ListUsersQuery)
        variables = {
        }
        operation_name = "ListUsers"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _ListVerifiedUsersQuery = """
    query ListVerifiedUsers {
  Users(where: {verified: {_eq: true}}) {
    id
    email
    given_name
    family_name
  }
}
    """

    def ListVerifiedUsers(self):
        query = gql(self._ListVerifiedUsersQuery)
        variables = {
        }
        operation_name = "ListVerifiedUsers"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
