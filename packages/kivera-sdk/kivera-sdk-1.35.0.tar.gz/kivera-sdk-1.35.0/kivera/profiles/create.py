from gql import gql
from typing import Sequence

class createMethods:

    _CreateProfileQuery = """
    mutation CreateProfile($description: String!, $name: String!, $organization_id: Int!) {
  insert_Profiles_one(object: {description: $description, name: $name, organization_id: $organization_id}) {
    description
    name
    id
    organization_id
  }
}
    """

    def CreateProfile(self, description: str, name: str, organization_id: int):
        query = gql(self._CreateProfileQuery)
        variables = {
            "description": description,
            "name": name,
            "organization_id": organization_id,
        }
        operation_name = "CreateProfile"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _CreateProfileV2Query = """
    mutation CreateProfileV2($description: String!, $name: String!, $organization_id: Int!, $tags: jsonb! = [], $rules: [ProfileRules_insert_input!] = []) {
  insert_Profiles(objects: {description: $description, name: $name, organization_id: $organization_id, tags: $tags, ProfileRules: {data: $rules}}) {
    returning {
      id
      description
      name
      organization_id
      tags
      ProfileRules {
        enforce
        deleted
        id
        profile_id
      }
    }
  }
}
    """

    def CreateProfileV2(self, description: str, name: str, organization_id: int, tags: dict = None, rules: Sequence[dict] = None):
        query = gql(self._CreateProfileV2Query)
        variables = {
            "description": description,
            "name": name,
            "organization_id": organization_id,
            "tags": tags,
            "rules": rules,
        }
        operation_name = "CreateProfileV2"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
