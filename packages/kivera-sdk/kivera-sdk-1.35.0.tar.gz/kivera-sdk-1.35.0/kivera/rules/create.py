from gql import gql
from typing import Sequence

class createMethods:

    _CreateRuleQuery = """
    mutation CreateRule($config: jsonb!,$description: String!, $service_id: Int!, $enable_cfn_scan: Boolean!, $enforce: Boolean!, $log_request_body: Boolean!) {
  insert_Rules_one(object: {config: $config, description: $description, service_id: $service_id, enable_cfn_scan: $enable_cfn_scan, enforce: $enforce, log_request_body: $log_request_body}) {
    config
    description
    id
    service_id
  }
}
    """

    def CreateRule(self, config: dict, description: str, service_id: int, enable_cfn_scan: bool, enforce: bool, log_request_body: bool):
        query = gql(self._CreateRuleQuery)
        variables = {
            "config": config,
            "description": description,
            "service_id": service_id,
            "enable_cfn_scan": enable_cfn_scan,
            "enforce": enforce,
            "log_request_body": log_request_body,
        }
        operation_name = "CreateRule"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _CreateRuleV4Query = """
    mutation CreateRuleV4(
  $config: jsonb = "",
  $description: String!,
  $service_id: Int!,
  $enable_cfn_scan: Boolean = false,
  $enforce: Boolean = true,
  $log_request_body: Boolean = true,
  $dependencies_enabled: Boolean = false,
  $tags: jsonb! = [],
  $rule_dependencies: [RuleDependencies_insert_input!] = [],
  $policy: String!,
  # @genqlient(pointer: true)
  $risk_rating: risk_rating_type = null,
  $compliance_mappings: jsonb! = [],
  $type_id: Int = 1
) {
  insert_Rules(objects: {
    config: $config,
    description: $description,
    service_id: $service_id,
    enable_cfn_scan: $enable_cfn_scan,
    enforce: $enforce,
    log_request_body: $log_request_body,
    dependencies_enabled: $dependencies_enabled,
    tags: $tags, RuleDependencies: {
      data: $rule_dependencies
    },
    policy: $policy,
    risk_rating: $risk_rating,
    compliance_mappings: $compliance_mappings,
    type_id: $type_id
  }) {
    returning {
      id
      log_request_body
      enforce
      enable_cfn_scan
      description
      dependencies_enabled
      service_id
      tags
      policy
      risk_rating
      compliance_mappings
      RuleDependencies {
        dependent_rule_id
        deleted
      }
      Service {
        GlobalService {
          provider_id
        }
      }
      RuleType {
        name
      }
    }
  }
}
    """

    def CreateRuleV4(self):
        query = gql(self._CreateRuleV4Query)
        variables = {
        }
        operation_name = "CreateRuleV4"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _CreateRulesQuery = """
    mutation CreateRules($objects: [Rules_insert_input!]!) {
  insert_Rules(objects: $objects) {
    returning {
      config
      description
      id
      service_id
      enforce
      enable_cfn_scan
      log_request_body
      tags
    }
  }
}
    """

    def CreateRules(self, objects: Sequence[dict]):
        query = gql(self._CreateRulesQuery)
        variables = {
            "objects": objects,
        }
        operation_name = "CreateRules"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _CreateRulesV4Query = """
    mutation CreateRulesV4($objects: [Rules_insert_input!]!) {
  insert_Rules(objects: $objects) {
    returning {
      config
      description
      id
      service_id
      enforce
      enable_cfn_scan
      log_request_body
      tags
      risk_rating
      compliance_mappings
      policy
    }
  }
}
    """

    def CreateRulesV4(self, objects: Sequence[dict]):
        query = gql(self._CreateRulesV4Query)
        variables = {
            "objects": objects,
        }
        operation_name = "CreateRulesV4"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
