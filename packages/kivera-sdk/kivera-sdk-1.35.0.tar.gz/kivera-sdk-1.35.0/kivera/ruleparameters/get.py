from gql import gql
from typing import Sequence

class getMethods:

    _GetRuleParameterQuery = """
    query GetRuleParameter($rule_parameter_id: Int!) {
    RuleParameters_by_pk(id: $rule_parameter_id) {
        parameter_name
        parameter_value
        rule_id
        id
    }
}
    """

    def GetRuleParameter(self, rule_parameter_id: int):
        query = gql(self._GetRuleParameterQuery)
        variables = {
            "rule_parameter_id": rule_parameter_id,
        }
        operation_name = "GetRuleParameter"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetRuleParameterV2Query = """
    query GetRuleParameterV2($rule_parameter_id: Int!) {
    RuleParameters_by_pk(id: $rule_parameter_id) {
        parameter_name
        parameter_value
        rule_id
        description
        id
    }
}
    """

    def GetRuleParameterV2(self, rule_parameter_id: int):
        query = gql(self._GetRuleParameterV2Query)
        variables = {
            "rule_parameter_id": rule_parameter_id,
        }
        operation_name = "GetRuleParameterV2"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetRuleParametersV4Query = """
    query GetRuleParametersV4($rule_id: Int!) {
    RuleParameters(where: {rule_id: {_eq: $rule_id}}) {
        rule_id
        parameter_value
        parameter_name
        id
        description
        Rule {
            id
            policy
        }
    }
}
    """

    def GetRuleParametersV4(self, rule_id: int):
        query = gql(self._GetRuleParametersV4Query)
        variables = {
            "rule_id": rule_id,
        }
        operation_name = "GetRuleParametersV4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
