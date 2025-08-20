from gql import gql
from typing import Sequence

class listMethods:

    _ListManagedRulesQuery = """
    query ListManagedRules {
    ManagedRules{
        id
        type_id
        description
        policy
        config
        tags
        version
        risk_rating
        compliance_mappings
        Service {
            id
            GlobalService {
                id
                name
                Provider {
                    id
                    name
                }
                Services {
                    id
                    inspection
                }
            }
        }
        enforce
        log_request_body
        created_at
        updated_at
    }
}
    """

    def ListManagedRules(self):
        query = gql(self._ListManagedRulesQuery)
        variables = {
        }
        operation_name = "ListManagedRules"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
