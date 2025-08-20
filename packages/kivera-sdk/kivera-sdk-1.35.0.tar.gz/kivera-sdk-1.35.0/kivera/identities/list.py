from gql import gql
from typing import Sequence

class listMethods:

    _ListIdentitiesQuery = """
    query ListIdentities {
  Identities(where: {status: {_eq: true}}) {
    config
    description
    name
    organization_id
    status
    tags
    id
    identity_type
    created_at
    updated_at
    UpdatedByUser {
      family_name
      given_name
      id
    }
    CreatedByUser {
      family_name
      id
      given_name
    }
    Counters_aggregate {
      aggregate {
        sum {
          counter_accepts
          counter_denials
          counter_notifies
          counter_total_request
        }
      }
    }
    IdentityProfiles_aggregate(where: {deleted: {_eq: false}})  {
      aggregate {
        count
      }
    }
    IdentityProfiles(where: {deleted: {_eq: false}}) {
      profile_id
      Profile  {
        ProfileRules_aggregate(where: {deleted: {_eq: false}}) {
          aggregate {
            count
          }
        }
      }
    }
    cloud_tenant {
      id
      name
    }
  }
}
    """

    def ListIdentities(self):
        query = gql(self._ListIdentitiesQuery)
        variables = {
        }
        operation_name = "ListIdentities"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
