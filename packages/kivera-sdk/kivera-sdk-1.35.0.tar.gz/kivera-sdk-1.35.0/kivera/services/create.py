from gql import gql
from typing import Sequence

class createMethods:

    _CreateServiceMappingQuery = """
    mutation CreateServiceMapping($objects: [Services_insert_input!]!) {
  insert_Services(
    objects: $objects,
    on_conflict: {
      constraint: services_org_id_global_service_id, update_columns: [inspection]
    }
  ) {
    returning {
      id
      organization_id
      inspection
      GlobalService {
        id
        provider_id
        Provider {
          name
        }
      }
    }
  }
}
    """

    def CreateServiceMapping(self, objects: Sequence[dict]):
        query = gql(self._CreateServiceMappingQuery)
        variables = {
            "objects": objects,
        }
        operation_name = "CreateServiceMapping"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
