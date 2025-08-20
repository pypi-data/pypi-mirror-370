from gql import gql
from typing import Sequence

class listMethods:

    _ListProxiesQuery = """
    query ListProxies {
  Proxies(where: {status: {_neq: "DELETED"}}) {
    id
    name
    description
    last_healthcheck_time
    organization_id
    status
    tags
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
    ProxyIdentities(where: {deleted: {_eq: false}, Identity: {status: {_eq: true}}}) {
      identity_id
    }
    ProxySettings {
      debug
      proxy_mode
      default_mode
      learning_mode
      allow_noncloud_traffic
      default_identity_id
      rego_raise_error
      on_error_action
      config_update_freq_secs
      idle_connection_timeout
      inspect_body_size_limit
    }
    ProxyDomainAcls {
      proxy_id
      DomainAcl {
        name
        id
        DomainAclEntries {
          id
          action
          domain
        }
      }
    }
    ProxyProviders {
      id
      provider_id
      proxy_id
      Provider {
        name
      }
      enabled
    }
    Counters_aggregate {
      aggregate {
        sum {
          counter_accepts
          counter_denials
          counter_notifies
          counter_total_request
        }
      }
    }
    ProxyDeployments(limit: 1, order_by: {id: desc}) {
      id
      config
      created_by_user_id
      date_created
      User {
        given_name
        family_name
        id
        email
      }
      config_version
      status
      proxy_id
      date_modified
      actioned_by_user_id
    }
  }
  Proxies_aggregate(where: {status: {_neq: "DELETED"}}) {
    aggregate {
      count
    }
  }
}
    """

    def ListProxies(self):
        query = gql(self._ListProxiesQuery)
        variables = {
        }
        operation_name = "ListProxies"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
