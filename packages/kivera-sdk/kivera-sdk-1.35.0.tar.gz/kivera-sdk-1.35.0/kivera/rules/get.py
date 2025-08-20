from gql import gql
from typing import Sequence

class getMethods:

    _GetRuleQuery = """
    query GetRule($rule_id: Int!) {
  Rules_by_pk(id: $rule_id) {
    id
    service_id
    type_id
    description
    config
  }
}
    """

    def GetRule(self, rule_id: int):
        query = gql(self._GetRuleQuery)
        variables = {
            "rule_id": rule_id,
        }
        operation_name = "GetRule"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetRuleV4Query = """
    query GetRuleV4($id: Int!) {
  Rules_by_pk(id: $id) {
    dependencies_enabled
    description
    enable_cfn_scan
    enforce
    log_request_body
    service_id
    config
    tags
    policy
    RuleDependencies {
      deleted
      dependent_rule_id
      id
      rule_id
    }
  }
}
    """

    def GetRuleV4(self, id: int):
        query = gql(self._GetRuleV4Query)
        variables = {
            "id": id,
        }
        operation_name = "GetRuleV4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetRulesAndPoliciesV4Query = """
    query GetRulesAndPoliciesV4($rule_id: Int!) {
  Rules(where: {id: {_eq: $rule_id}}) {
    id
    service_id
    type_id
    description
    config
    enable_cfn_scan
    enforce
    log_request_body
    dependencies_enabled
    tags
    risk_rating
    compliance_mappings
    policy
    ImportedFrom {
      id
      version
    }
    version
    Service {
      id
      GlobalService {
        id
        name
        Provider {
          id
          name
        }
      }
    }
  }
}
    """

    def GetRulesAndPoliciesV4(self, rule_id: int):
        query = gql(self._GetRulesAndPoliciesV4Query)
        variables = {
            "rule_id": rule_id,
        }
        operation_name = "GetRulesAndPoliciesV4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetRulesByImportedFromIDsQuery = """
    query GetRulesByImportedFromIDs($imported_from: [Int!]!) {
  Rules(where: {ImportedFrom: {id: {_in: $imported_from}}}) {
    id
    description
    imported_from
    service_id
    type_id
    version
  }
}
    """

    def GetRulesByImportedFromIDs(self, imported_from: Sequence[int]):
        query = gql(self._GetRulesByImportedFromIDsQuery)
        variables = {
            "imported_from": imported_from,
        }
        operation_name = "GetRulesByImportedFromIDs"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetServiceRuleIDsQuery = """
    query GetServiceRuleIDs($serviceID: Int!) {
  Rules(where: {service_id: {_eq: $serviceID}}) {
    id
  }
}
    """

    def GetServiceRuleIDs(self, serviceID: int):
        query = gql(self._GetServiceRuleIDsQuery)
        variables = {
            "serviceID": serviceID,
        }
        operation_name = "GetServiceRuleIDs"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetServiceRulesQuery = """
    query GetServiceRules($serviceID: Int!) {
  Rules(where: {service_id: {_eq: $serviceID}}) {
    id
    description
    config
    Service {
      GlobalService {
        Provider {
          id
          name
        }
      }
    }
    ruleDependenciesByRuleId {
      dependent_rule_id
      deleted
      RuleDependenciesResources {
        locked
        id
        rule_dependencies_id
      }
    }
  }
}
    """

    def GetServiceRules(self, serviceID: int):
        query = gql(self._GetServiceRulesQuery)
        variables = {
            "serviceID": serviceID,
        }
        operation_name = "GetServiceRules"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
