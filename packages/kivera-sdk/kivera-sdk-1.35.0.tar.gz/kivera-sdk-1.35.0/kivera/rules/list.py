from gql import gql
from typing import Sequence

class listMethods:

    _ListRulesV4Query = """
    query ListRulesV4 {
  Rules {
    id
    service_id
    type_id
    description
    enable_cfn_scan
    enforce
    log_request_body
    policy
    config
    dependencies_enabled
    tags
    risk_rating
    compliance_mappings
    version
    created_at
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
    ImportedFrom{
      id
      version
    }
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
    ProfileRules_aggregate(where: {deleted: {_eq: false}})  {
      aggregate {
        count
      }
    }
    RuleDependencies(where: {deleted: {_eq: false}}) {
      id
      rule_id
      dependent_rule_id
      ruleByRuleId {
        id
        dependencies_enabled
      }
    }
    ruleDependenciesByRuleId(where: {deleted: {_eq: false}}) {
      dependent_rule_id
      rule_id
      RuleDependenciesResources {
        locked
        rule_dependencies_id
      }
    }
  }
}
    """

    def ListRulesV4(self):
        query = gql(self._ListRulesV4Query)
        variables = {
        }
        operation_name = "ListRulesV4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
