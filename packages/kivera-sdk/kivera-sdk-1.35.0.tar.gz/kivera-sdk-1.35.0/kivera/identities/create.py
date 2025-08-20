from gql import gql
from typing import Sequence

class createMethods:

    _CreateAwsTenantIdentityQuery = """
    mutation CreateAwsTenantIdentity($name: String!, $description: String!, $organization_id: Int!, $tags: jsonb! = [], $identity_type: identity_type!, $profiles: [IdentityProfiles_insert_input!] = []) {
  insert_Identities(objects: {
    name: $name,
    description: $description,
    organization_id: $organization_id,
    tags: $tags,
    identity_type: $identity_type,
    IdentityProfiles: {data: $profiles},
    AwsTenants: {data: {}},
  }){
    returning {
      id
      name
      description
      organization_id
      status
      tags
      identity_type
      AwsTenants {
        id
        account_id
        unique_id
        verified
        identity_id
        provider_id
        role_arn
      }
    }
  }
}
    """

    def CreateAwsTenantIdentity(self, name: str, description: str, organization_id: int, identity_type: dict, tags: dict = None, profiles: Sequence[dict] = None):
        query = gql(self._CreateAwsTenantIdentityQuery)
        variables = {
            "name": name,
            "description": description,
            "organization_id": organization_id,
            "tags": tags,
            "identity_type": identity_type,
            "profiles": profiles,
        }
        operation_name = "CreateAwsTenantIdentity"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _CreateIdentityQuery = """
    mutation CreateIdentity($name: String!, $description: String!, $config: jsonb!, $organization_id: Int!, $tags: jsonb!, $identity_type: identity_type!, $profiles: [IdentityProfiles_insert_input!] = []) {
  insert_Identities(objects: {
    name: $name,
    config: $config,
    description: $description,
    organization_id: $organization_id,
    status: true,
    tags: $tags,
    identity_type: $identity_type,
    IdentityProfiles: {data: $profiles}}) {
    returning {
      description
      organization_id
      status
      config
      id
      name
      tags
    }
  }
}
    """

    def CreateIdentity(self, name: str, description: str, config: dict, organization_id: int, tags: dict, identity_type: dict, profiles: Sequence[dict] = None):
        query = gql(self._CreateIdentityQuery)
        variables = {
            "name": name,
            "description": description,
            "config": config,
            "organization_id": organization_id,
            "tags": tags,
            "identity_type": identity_type,
            "profiles": profiles,
        }
        operation_name = "CreateIdentity"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
