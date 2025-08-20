from gql import gql
from typing import Sequence

class attachMethods:

    _AttachDependentRulesToRuleQuery = """
    mutation AttachDependentRulesToRule($objects: [RuleDependencies_insert_input!]!) {
    insert_RuleDependencies(objects: $objects, on_conflict: {constraint: ruledependencies_rule_id_dependent_rule_id_uniq_key, update_columns: [deleted]}) {
        returning {
            dependent_rule_id
            id
        }
    }
}
    """

    def AttachDependentRulesToRule(self, objects: Sequence[dict]):
        query = gql(self._AttachDependentRulesToRuleQuery)
        variables = {
            "objects": objects,
        }
        operation_name = "AttachDependentRulesToRule"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
