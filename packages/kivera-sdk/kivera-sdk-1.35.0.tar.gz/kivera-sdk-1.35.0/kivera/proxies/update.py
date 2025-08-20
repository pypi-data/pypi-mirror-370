from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateProxyQuery = """
    mutation UpdateProxy($description: String!, $name: String!, $debug: Boolean!, $id: Int!, $proxy_mode: String!, $default_identity_id: Int, $provider_id: Int!) {
  update_Proxies_by_pk(pk_columns: {id: $id}, _set: {description: $description, name: $name}) {
    id
  }
  update_ProxySettings(where: {proxy_id: {_eq: $id}}, _set: {debug: $debug, proxy_mode: $proxy_mode, default_identity_id: $default_identity_id}) {
    returning {
      id
      proxy_mode
      default_identity_id
      debug
    }
  }
  update_ProxyProviders(where: {proxy_id: {_eq: $id}}, _set: {provider_id: $provider_id}) {
    returning {
      provider_id
      proxy_id
      id
    }
  }
}
    """

    def UpdateProxy(self, description: str, name: str, debug: bool, id: int, proxy_mode: str, provider_id: int, default_identity_id: int = None):
        query = gql(self._UpdateProxyQuery)
        variables = {
            "description": description,
            "name": name,
            "debug": debug,
            "id": id,
            "proxy_mode": proxy_mode,
            "default_identity_id": default_identity_id,
            "provider_id": provider_id,
        }
        operation_name = "UpdateProxy"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyAllownoncloudtrafficQuery = """
    mutation UpdateProxyAllownoncloudtraffic($proxy_id: Int!, $allow_noncloud_traffic: Boolean!) {
  update_ProxySettings(where: {proxy_id: {_eq: $proxy_id}}, _set: {allow_noncloud_traffic: $allow_noncloud_traffic}) {
    returning {
      id
      proxy_id
      allow_noncloud_traffic
    }
  }
}
    """

    def UpdateProxyAllownoncloudtraffic(self, proxy_id: int, allow_noncloud_traffic: bool):
        query = gql(self._UpdateProxyAllownoncloudtrafficQuery)
        variables = {
            "proxy_id": proxy_id,
            "allow_noncloud_traffic": allow_noncloud_traffic,
        }
        operation_name = "UpdateProxyAllownoncloudtraffic"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyCloudProviderQuery = """
    mutation UpdateProxyCloudProvider($enabled: Boolean!, $proxy_id: Int!, $provider_id: Int!) {
  update_ProxyProviders(where: {proxy_id: {_eq: $proxy_id}, provider_id: {_eq: $provider_id}}, _set: {enabled: $enabled}) {
    returning {
      enabled
      provider_id
      proxy_id
      id
    }
  }
}
    """

    def UpdateProxyCloudProvider(self, enabled: bool, proxy_id: int, provider_id: int):
        query = gql(self._UpdateProxyCloudProviderQuery)
        variables = {
            "enabled": enabled,
            "proxy_id": proxy_id,
            "provider_id": provider_id,
        }
        operation_name = "UpdateProxyCloudProvider"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyDescriptionQuery = """
    mutation UpdateProxyDescription($description: String!, $id: Int!) {
  update_Proxies_by_pk(_set: {description: $description}, pk_columns: {id: $id}) {
    name
    description
    id
  }
}
    """

    def UpdateProxyDescription(self, description: str, id: int):
        query = gql(self._UpdateProxyDescriptionQuery)
        variables = {
            "description": description,
            "id": id,
        }
        operation_name = "UpdateProxyDescription"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyHealthCheckTimeQuery = """
    mutation UpdateProxyHealthCheckTime($proxy_id: Int!) {
  __typename
  update_Proxies_by_pk(pk_columns: {id: $proxy_id} , _set: {last_healthcheck_time: "now()"}) {
    id
    last_healthcheck_time
  }
}
    """

    def UpdateProxyHealthCheckTime(self, proxy_id: int):
        query = gql(self._UpdateProxyHealthCheckTimeQuery)
        variables = {
            "proxy_id": proxy_id,
        }
        operation_name = "UpdateProxyHealthCheckTime"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyLearningModeQuery = """
    mutation UpdateProxyLearningMode($proxy_id: Int!, $default_mode: proxysettings_default_mode_type!) {
  update_ProxySettings(where: {proxy_id: {_eq: $proxy_id}}, _set: {default_mode: $default_mode}) {
    returning {
      id
      proxy_id
      default_mode
    }
  }
}
    """

    def UpdateProxyLearningMode(self, proxy_id: int, default_mode: dict):
        query = gql(self._UpdateProxyLearningModeQuery)
        variables = {
            "proxy_id": proxy_id,
            "default_mode": default_mode,
        }
        operation_name = "UpdateProxyLearningMode"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyLogLevelQuery = """
    mutation UpdateProxyLogLevel($proxy_id: Int!, $logLevel: Boolean!) {
  update_ProxySettings(where:{proxy_id: {_eq: $proxy_id}}, _set: {debug: $logLevel}){
    returning{
      id
      proxy_id
      debug
    }
  }
}
    """

    def UpdateProxyLogLevel(self, proxy_id: int, logLevel: bool):
        query = gql(self._UpdateProxyLogLevelQuery)
        variables = {
            "proxy_id": proxy_id,
            "logLevel": logLevel,
        }
        operation_name = "UpdateProxyLogLevel"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyNameQuery = """
    mutation UpdateProxyName($name: String!, $id: Int!) {
  update_Proxies_by_pk(_set: {name: $name}, pk_columns: {id: $id}) {
    name
    id
  }
}
    """

    def UpdateProxyName(self, name: str, id: int):
        query = gql(self._UpdateProxyNameQuery)
        variables = {
            "name": name,
            "id": id,
        }
        operation_name = "UpdateProxyName"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyStatusQuery = """
    mutation UpdateProxyStatus($proxy_id: Int!, $status: String) {
    update_Proxies(where: {id: {_eq: $proxy_id }}, _set: { status: $status }) {
        returning {
            id
            status
        }
    }
}
    """

    def UpdateProxyStatus(self, proxy_id: int, status: str = None):
        query = gql(self._UpdateProxyStatusQuery)
        variables = {
            "proxy_id": proxy_id,
            "status": status,
        }
        operation_name = "UpdateProxyStatus"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateProxyV2Query = """
    mutation UpdateProxyV2(
  $id: Int!,
  $name: String!,
  $description: String!,
  $debug: Boolean = false,
  $proxy_mode: String = "HYBRID",
  $default_mode: proxysettings_default_mode_type!,
  $learning_mode: Boolean!,
  # @genqlient(pointer: true)
  $default_identity_id: Int = null,
  $allow_noncloud_traffic: Boolean = false,
  $tags: jsonb! = [],
  $providers: [ProxyProviders_insert_input!] = [],
  $identities: [ProxyIdentities_insert_input!] = [],
  $domain_acls: [ProxyDomainAcls_insert_input!] = [],
  $rego_raise_error: Boolean = false,
  $on_error_action: rule_evaluation_action!,
  $config_update_freq_secs: Int! = 10,
  $idle_connection_timeout: Int! = 30,
  $inspect_body_size_limit: Int! = 10000000
) {
  update_Proxies(where: {id: {_eq: $id}}, _set: {description: $description, name: $name, tags: $tags}) {
    returning {
      id
      description
      name
      organization_id
      status
      last_healthcheck_time
    }
  }
  update_ProxySettings(where: {proxy_id: {_eq: $id}}, _set: {
      debug: $debug,
      proxy_mode: $proxy_mode,
      default_identity_id: $default_identity_id,
      allow_noncloud_traffic: $allow_noncloud_traffic,
      default_mode: $default_mode,
      learning_mode: $learning_mode,
      rego_raise_error: $rego_raise_error,
      on_error_action:$on_error_action,
      config_update_freq_secs: $config_update_freq_secs,
      idle_connection_timeout: $idle_connection_timeout,
      inspect_body_size_limit: $inspect_body_size_limit
    }) {
    returning {
      id
      debug
      proxy_mode
      default_mode
      learning_mode
      default_identity_id
      rego_raise_error
      on_error_action
      config_update_freq_secs
      idle_connection_timeout
      inspect_body_size_limit
    }
  }
  insert_ProxyProviders(objects: $providers, on_conflict: {constraint: proxyproviders_uniq_key, update_columns: [provider_id, enabled]}) {
    returning {
      id
      provider_id
    }
  }
  insert_ProxyIdentities(objects: $identities, on_conflict: {constraint: proxyidentities_uniq_key, update_columns: [identity_id, deleted]}) {
    returning {
      id
      deleted
      identity_id
    }
  }
  delete_ProxyDomainAcls(where: {proxy_id: {_eq: $id}}) {
    affected_rows
  }
  insert_ProxyDomainAcls(objects: $domain_acls) {
    affected_rows
    returning {
      id
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
  }
}
    """

    def UpdateProxyV2(self):
        query = gql(self._UpdateProxyV2Query)
        variables = {
        }
        operation_name = "UpdateProxyV2"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
