from gql import gql
from typing import Sequence

class getMethods:

    _GetUserByIdQuery = """
    query GetUserById($user_id: String!) {
  Users_by_pk(id: $user_id) {
    id
    verified
    email
    given_name
    family_name
    created_at
    timezone
    country_iso_code
    Memberships {
      id
      Organization {
        company_name
        id
        beta_access
        Plan {
          id
          name
          proxy_limit
        }
      }
    }
  }
}
    """

    def GetUserById(self, user_id: str):
        query = gql(self._GetUserByIdQuery)
        variables = {
            "user_id": user_id,
        }
        operation_name = "GetUserById"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetUserDetailsQuery = """
    query GetUserDetails($email: String!) {
  Users(where: {email: {_eq: $email}}) {
    id
    verified
    email
    given_name
    family_name
    created_at
    timezone
    country_iso_code
    Memberships {
      id
      Organization {
        company_name
        id
        beta_access
      }
    }
  }
}
    """

    def GetUserDetails(self, email: str):
        query = gql(self._GetUserDetailsQuery)
        variables = {
            "email": email,
        }
        operation_name = "GetUserDetails"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
