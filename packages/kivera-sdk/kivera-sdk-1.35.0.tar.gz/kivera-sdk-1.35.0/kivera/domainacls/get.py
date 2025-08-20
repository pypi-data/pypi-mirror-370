from gql import gql
from typing import Sequence

class getMethods:

    _GetDomainACLQuery = """
    query GetDomainACL($id: Int!) {
    DomainAcls_by_pk(id: $id) {
        DomainAclEntries {
            action
            domain
            domain_acl_id
            id
        }
        created_at
        default_action
        id
        name
        organization_id
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
        ProxyDomainAcls {
            Proxy {
                id
                name
            }
        }
    }
}
    """

    def GetDomainACL(self, id: int):
        query = gql(self._GetDomainACLQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetDomainACL"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
