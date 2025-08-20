from gql import gql
from typing import Sequence

class getMethods:

    _GetProfileQuery = """
    query GetProfile($profile_id: Int!) {
  Profiles_by_pk(id: $profile_id) {
    description
    id
    name
    organization_id
  }
}
    """

    def GetProfile(self, profile_id: int):
        query = gql(self._GetProfileQuery)
        variables = {
            "profile_id": profile_id,
        }
        operation_name = "GetProfile"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProfileAndIdentityProfilesQuery = """
    query GetProfileAndIdentityProfiles($profile_id: Int!) {
  Profiles_by_pk(id: $profile_id) {
    id
    description
    name
    organization_id
    tags
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
    ProfileRules(where: {deleted: {_eq: false}}) {
      rule_id
    }
    IdentityProfiles(where: {deleted: {_eq: false}})  {
      Identity {
        name
      }
    }
    IdentityProfiles_aggregate(where: { deleted: { _eq: false } }) {
      aggregate {
        count
      }
    }
    ProfileRules_aggregate(where: { deleted: { _eq: false } }) {
      aggregate {
        count
      }
    }
  }
  Rules_aggregate {
    aggregate {
      count
    }
  }
}
    """

    def GetProfileAndIdentityProfiles(self, profile_id: int):
        query = gql(self._GetProfileAndIdentityProfilesQuery)
        variables = {
            "profile_id": profile_id,
        }
        operation_name = "GetProfileAndIdentityProfiles"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProfileAndRulesQuery = """
    query GetProfileAndRules($profile_id: Int!) {
  Profiles_by_pk(id: $profile_id) {
    description
    id
    name
    organization_id
    tags
    ProfileRules(where: {deleted: {_eq: false}})  {
      rule_id
      profile_id
    }
  }
}
    """

    def GetProfileAndRules(self, profile_id: int):
        query = gql(self._GetProfileAndRulesQuery)
        variables = {
            "profile_id": profile_id,
        }
        operation_name = "GetProfileAndRules"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetProfileV2Query = """
    query GetProfileV2($id: Int!) {
  Profiles_by_pk(id: $id) {
    description
    name
    organization_id
    id
    tags
    ProfileRules(where: {deleted: {_eq: false}}) {
      deleted
      enforce
      profile_id
      rule_id
    }
  }
}
    """

    def GetProfileV2(self, id: int):
        query = gql(self._GetProfileV2Query)
        variables = {
            "id": id,
        }
        operation_name = "GetProfileV2"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
