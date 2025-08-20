from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteIdentitiesQuery = """
    mutation DeleteIdentities($ids: [Int!]!) {
  update_Identities(where: {id: {_in: $ids}}, _set: {status: false}) {
    returning {
      id
      status
    }
  }
  update_IdentityProfiles(where: {identity_id: {_in: $ids}}, _set: {deleted: true}) {
    affected_rows
  }
  update_ProxyIdentities(where: {identity_id: {_in: $ids}}, _set: {deleted: true}) {
    affected_rows
  }
}
    """

    def DeleteIdentities(self, ids: Sequence[int]):
        query = gql(self._DeleteIdentitiesQuery)
        variables = {
            "ids": ids,
        }
        operation_name = "DeleteIdentities"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _DeleteIdentityQuery = """
    mutation DeleteIdentity($id: Int!) {
  update_Identities(where: {id: {_eq: $id}}, _set: {status: false}) {
    returning {
      config
      description
      id
      name
      organization_id
      status
      tags
    }
  }
  update_IdentityProfiles(where: {identity_id: {_eq: $id}}, _set: {deleted: true}) {
    affected_rows
  }
  update_ProxyIdentities(where: {identity_id: {_eq: $id}}, _set: {deleted: true}) {
    affected_rows
  }
}
    """

    def DeleteIdentity(self, id: int):
        query = gql(self._DeleteIdentityQuery)
        variables = {
            "id": id,
        }
        operation_name = "DeleteIdentity"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
