from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteDomainACLQuery = """
    mutation DeleteDomainACL($id: Int!) {
    delete_DomainAclEntries(where: {domain_acl_id: {_eq: $id}}) {
        affected_rows
    }
    delete_DomainAcls_by_pk(id: $id) {
        id
    }
}
    """

    def DeleteDomainACL(self, id: int):
        query = gql(self._DeleteDomainACLQuery)
        variables = {
            "id": id,
        }
        operation_name = "DeleteDomainACL"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
