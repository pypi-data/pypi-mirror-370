from gql import gql
from typing import Sequence

class getMethods:

    _GetRuleDependencyResourcesQuery = """
    query GetRuleDependencyResources($id: Int!) {
    RuleDependenciesResources(where: {id: {_eq: $id}}) {
        id
        locked
        resource_id
        rule_dependencies_id
        RuleDependency {
            rule_id
            dependent_rule_id
        }
    }
}
    """

    def GetRuleDependencyResources(self, id: int):
        query = gql(self._GetRuleDependencyResourcesQuery)
        variables = {
            "id": id,
        }
        operation_name = "GetRuleDependencyResources"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetRuleDependencyResourcesByRuleIDQuery = """
    query GetRuleDependencyResourcesByRuleID($identity_id: Int!, $rule_ids: [Int!]!) {
    RuleDependenciesResources(where: {identity_id: {_eq: $identity_id}, RuleDependency: {rule_id: {_in: $rule_ids}}}) {
        id
        identity_id
        locked
        resource_id
        rule_dependencies_id
        RuleDependency {
            rule_id
            dependent_rule_id
        }
    }
}
    """

    def GetRuleDependencyResourcesByRuleID(self, identity_id: int, rule_ids: Sequence[int]):
        query = gql(self._GetRuleDependencyResourcesByRuleIDQuery)
        variables = {
            "identity_id": identity_id,
            "rule_ids": rule_ids,
        }
        operation_name = "GetRuleDependencyResourcesByRuleID"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
