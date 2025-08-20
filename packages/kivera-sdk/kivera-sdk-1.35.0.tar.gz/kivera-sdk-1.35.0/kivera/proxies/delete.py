from gql import gql
from typing import Sequence

class deleteMethods:

    _DeleteProxiesQuery = """
    mutation DeleteProxies($ids: [Int!]!) {
  update_Proxies(where: {id: {_in: $ids}}, _set: {status: "DELETING"}) {
    returning {
      status
      id
    }
  }
  update_ProxyIdentities(where: {proxy_id: {_in: $ids}}, _set: {deleted: true}) {
    affected_rows
  }
}
    """

    def DeleteProxies(self, ids: Sequence[int]):
        query = gql(self._DeleteProxiesQuery)
        variables = {
            "ids": ids,
        }
        operation_name = "DeleteProxies"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _DeleteProxyQuery = """
    mutation DeleteProxy($id: Int!) {
  update_Proxies(where: {id: {_eq: $id}}, _set: {status: "DELETING"}) {
    returning {
      status
      id
    }
  }
}
    """

    def DeleteProxy(self, id: int):
        query = gql(self._DeleteProxyQuery)
        variables = {
            "id": id,
        }
        operation_name = "DeleteProxy"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _DeleteProxyV2Query = """
    mutation DeleteProxyV2($id: Int!) {
  update_Proxies(where: {id: {_eq: $id}}, _set: {status: "DELETING"}) {
    returning {
      status
      id
    }
  }
  delete_ProxyDomainAcls(where: {proxy_id: {_eq: $id}}){
    affected_rows
  }
  update_ProxyIdentities(where: {proxy_id: {_eq: $id}}, _set: {deleted: true}) {
    affected_rows
  }
}
    """

    def DeleteProxyV2(self, id: int):
        query = gql(self._DeleteProxyV2Query)
        variables = {
            "id": id,
        }
        operation_name = "DeleteProxyV2"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
