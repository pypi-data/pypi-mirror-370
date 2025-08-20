from gql import gql
from typing import Sequence

class listMethods:

    _ListDomainACLsQuery = """
    query ListDomainACLs {
    DomainAcls {
        id
        organization_id
        name
        default_action
        created_at
        updated_at
        DomainAclEntries {
            action
            domain
            domain_acl_id
            id
        }
        UpdatedByUser {
            id
            given_name
            family_name
        }
        CreatedByUser {
            id
            given_name
            family_name
        }
    }
}
    """

    def ListDomainACLs(self):
        query = gql(self._ListDomainACLsQuery)
        variables = {
        }
        operation_name = "ListDomainACLs"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
