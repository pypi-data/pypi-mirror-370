from gql import gql
from typing import Sequence

class getMethods:

    _GetOrganizationQuery = """
    query GetOrganization($org_id: Int!) {
  Organizations(where: {id: {_eq: $org_id}}) {
    technical_contact
    plan_id
    max_total_request_count
    id
    email_domain
    domain
    company_name
    billing_contact
    Plan {
      name
      max_total_request_count
      instance_size
      max_instance_count
      min_instance_count
      proxy_limit
    }
    allowed_domains
    enforce_mfa
  }
}
    """

    def GetOrganization(self, org_id: int):
        query = gql(self._GetOrganizationQuery)
        variables = {
            "org_id": org_id,
        }
        operation_name = "GetOrganization"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _GetOrganizationAllowedDomainsQuery = """
    query GetOrganizationAllowedDomains($org_id: Int!) {
  Organizations(where: {id: {_eq: $org_id}}) {
    allowed_domains
    enforce_mfa
  }
}
    """

    def GetOrganizationAllowedDomains(self, org_id: int):
        query = gql(self._GetOrganizationAllowedDomainsQuery)
        variables = {
            "org_id": org_id,
        }
        operation_name = "GetOrganizationAllowedDomains"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
