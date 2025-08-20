from gql import gql
from typing import Sequence

class attachMethods:

    _AttachRuleToProfileQuery = """
    mutation AttachRuleToProfile($profile_id: Int!, $rule_id: Int!) {
  insert_ProfileRules(objects: {profile_id: $profile_id, rule_id: $rule_id}) {
    returning {
      Rule {
        id
      }
      Profile {
        id
      }
    }
  }
}
    """

    def AttachRuleToProfile(self, profile_id: int, rule_id: int):
        query = gql(self._AttachRuleToProfileQuery)
        variables = {
            "profile_id": profile_id,
            "rule_id": rule_id,
        }
        operation_name = "AttachRuleToProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _AttachRulesToProfileQuery = """
    mutation AttachRulesToProfile($objects: [ProfileRules_insert_input!]!, $profile_id: Int!) {
  delete_ProfileRules(where: {profile_id: {_eq: $profile_id}}) {
    returning {
      enforce
      id
      profile_id
      rule_id
    }
  }
  insert_ProfileRules(objects: $objects){
    returning{
      id
      rule_id
    }
  }
}
    """

    def AttachRulesToProfile(self, objects: Sequence[dict], profile_id: int):
        query = gql(self._AttachRulesToProfileQuery)
        variables = {
            "objects": objects,
            "profile_id": profile_id,
        }
        operation_name = "AttachRulesToProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
