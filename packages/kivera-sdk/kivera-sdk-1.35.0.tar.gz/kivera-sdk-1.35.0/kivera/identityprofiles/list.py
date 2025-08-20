from gql import gql
from typing import Sequence

class listMethods:

    _GetIdentityProfilesQuery = """
    query GetIdentityProfiles {
  IdentityProfiles(where: {deleted: {_eq: false}}) {
    deleted
    id
    identity_id
    profile_id
  }
}
    """

    def GetIdentityProfiles(self):
        query = gql(self._GetIdentityProfilesQuery)
        variables = {
        }
        operation_name = "GetIdentityProfiles"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
