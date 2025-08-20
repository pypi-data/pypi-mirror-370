from gql import gql
from typing import Sequence

class getMethods:

    _GetRulePoliciesConfigActionsV4Query = """
    query GetRulePoliciesConfigActionsV4($serviceID: Int!) {
    Rules(where: {service_id: {_eq: $serviceID}}) {
        id
        config
        policy
    }
}
    """

    def GetRulePoliciesConfigActionsV4(self, serviceID: int):
        query = gql(self._GetRulePoliciesConfigActionsV4Query)
        variables = {
            "serviceID": serviceID,
        }
        operation_name = "GetRulePoliciesConfigActionsV4"
        operation_type = "read"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
