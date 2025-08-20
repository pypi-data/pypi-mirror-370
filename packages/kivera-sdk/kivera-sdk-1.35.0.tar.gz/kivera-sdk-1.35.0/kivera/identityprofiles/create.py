from gql import gql
from typing import Sequence

class createMethods:

    _CreateIdentityProfileQuery = """
    mutation CreateIdentityProfile($identity_id: Int!, $profile_id: Int!) {
  insert_IdentityProfiles(objects: {identity_id: $identity_id, profile_id: $profile_id, deleted: false}) {
    returning {
      deleted
      identity_id
      profile_id
    }
  }
}
    """

    def CreateIdentityProfile(self, identity_id: int, profile_id: int):
        query = gql(self._CreateIdentityProfileQuery)
        variables = {
            "identity_id": identity_id,
            "profile_id": profile_id,
        }
        operation_name = "CreateIdentityProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
