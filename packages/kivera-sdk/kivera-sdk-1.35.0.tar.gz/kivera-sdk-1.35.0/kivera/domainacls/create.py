from gql import gql
from typing import Sequence

class createMethods:

    _CreateDomainACLQuery = """
    mutation CreateDomainACL($name: String!, $default_action: domain_acl_actions!, $organization_id: Int!, $objects: [DomainAclEntries_insert_input!]!) {
    insert_DomainAcls_one(object: {
        default_action: $default_action,
        name: $name,
        organization_id: $organization_id,
        DomainAclEntries: {data: $objects}
    }) {
        id
        name
    }
}
    """

    def CreateDomainACL(self, name: str, default_action: dict, organization_id: int, objects: Sequence[dict]):
        query = gql(self._CreateDomainACLQuery)
        variables = {
            "name": name,
            "default_action": default_action,
            "organization_id": organization_id,
            "objects": objects,
        }
        operation_name = "CreateDomainACL"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
