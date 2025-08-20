from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateDomainACLQuery = """
    mutation UpdateDomainACL($id: Int!, $name: String!, $default_action: domain_acl_actions!, $insert_objects: [DomainAclEntries_insert_input!] = []) {
    update_DomainAcls_by_pk(pk_columns: {id: $id}, _set: {name: $name, default_action: $default_action}) {
        name
        default_action
    }
    delete_DomainAclEntries(where: {domain_acl_id: {_eq: $id}}) {
        affected_rows
    }
    insert_DomainAclEntries(objects: $insert_objects) {
        affected_rows
    }
}
    """

    def UpdateDomainACL(self, id: int, name: str, default_action: dict, insert_objects: Sequence[dict] = None):
        query = gql(self._UpdateDomainACLQuery)
        variables = {
            "id": id,
            "name": name,
            "default_action": default_action,
            "insert_objects": insert_objects,
        }
        operation_name = "UpdateDomainACL"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
