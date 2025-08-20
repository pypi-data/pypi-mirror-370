from gql import gql
from typing import Sequence

class getMethods:

    _GetIdentityProfileQuery = """
    query GetIdentityProfile($id: Int!) {
  IdentityProfiles_by_pk(id: $id) {
    deleted
    id
    identity_id
    profile_id
  }
}
    """

    def GetIdentityProfile(self, id: int):
        query = gql(self._GetIdentityProfileQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetIdentityProfile"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
