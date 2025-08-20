from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteProfileQuery = """
    mutation DeleteProfile($profile_id: Int!) {
  delete_ProfileRules(where: {profile_id: {_eq: $profile_id}}) {
    returning {
      id
    }
  }
  delete_IdentityProfiles(where: {profile_id: {_eq: $profile_id}}) {
    returning {
      identity_id
      profile_id
      deleted
    }
  }
  delete_Profiles_by_pk(id: $profile_id) {
    description
    id
    name
    organization_id
  }
}
    """

    def DeleteProfile(self, profile_id: int):
        query = gql(self._DeleteProfileQuery)
        variables = {
            "profile_id": profile_id,
        }
        operation_name = "DeleteProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _DeleteProfilesQuery = """
    mutation DeleteProfiles($ids: [Int!]!) {
  delete_ProfileRules(where: {profile_id: {_in: $ids}}) {
    affected_rows
  }
  delete_IdentityProfiles(where: {profile_id: {_in: $ids}}) {
    affected_rows
  }
  delete_Profiles(where: {id: {_in: $ids}}){
    affected_rows
  }
}
    """

    def DeleteProfiles(self, ids: Sequence[int]):
        query = gql(self._DeleteProfilesQuery)
        variables = {
            "ids": ids,
        }
        operation_name = "DeleteProfiles"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _DeleteRuleFromProfileQuery = """
    mutation DeleteRuleFromProfile($profile_id: Int!, $rule_id: Int!) {
  delete_ProfileRules(where: {profile_id: {_eq: $profile_id}, rule_id: {_eq: $rule_id}}) {
    returning {
      enforce
      id
      profile_id
      rule_id
    }
  }
}
    """

    def DeleteRuleFromProfile(self, profile_id: int, rule_id: int):
        query = gql(self._DeleteRuleFromProfileQuery)
        variables = {
            "profile_id": profile_id,
            "rule_id": rule_id,
        }
        operation_name = "DeleteRuleFromProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _DeleteRulesFromProfileQuery = """
    mutation DeleteRulesFromProfile($profile_id: Int!) {
  delete_ProfileRules(where: {profile_id: {_eq: $profile_id}}) {
    returning {
      enforce
      id
      profile_id
      rule_id
    }
  }
}
    """

    def DeleteRulesFromProfile(self, profile_id: int):
        query = gql(self._DeleteRulesFromProfileQuery)
        variables = {
            "profile_id": profile_id,
        }
        operation_name = "DeleteRulesFromProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
