from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateProfileQuery = """
    mutation UpdateProfile($id: Int!, $name: String!, $description: String!) {
  update_Profiles_by_pk(pk_columns: {id: $id}, _set: {description: $description, name: $name}) {
    description
    id
    name
  }
}
    """

    def UpdateProfile(self, id: int, name: str, description: str):
        query = gql(self._UpdateProfileQuery)
        variables = {
            "id": id,
            "name": name,
            "description": description,
        }
        operation_name = "UpdateProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProfileV2Query = """
    mutation UpdateProfileV2($id: Int!, $description: String!, $name: String!, $rules: [ProfileRules_insert_input!] = [], $tags: jsonb! = []) {
  update_Profiles(where: {id: {_eq: $id}}, _set: {description: $description, name: $name, tags: $tags}) {
    returning {
      description
      organization_id
      tags
    }
  }
  insert_ProfileRules(objects: $rules, on_conflict: {constraint: profilerules_uniq_key, update_columns: [rule_id,deleted]}) {
    returning {
      deleted
      enforce
      id
      profile_id
      rule_id
    }
  }
}
    """

    def UpdateProfileV2(self, id: int, description: str, name: str, rules: Sequence[dict] = None, tags: dict = None):
        query = gql(self._UpdateProfileV2Query)
        variables = {
            "id": id,
            "description": description,
            "name": name,
            "rules": rules,
            "tags": tags,
        }
        operation_name = "UpdateProfileV2"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
