from gql import gql
from typing import Sequence

class updateMethods:

    _UpdateUserQuery = """
    mutation UpdateUser($user_id: String!, $changes: Users_set_input!) {
  update_Users_by_pk(pk_columns: {id: $user_id}, _set: $changes) {
    id
    email
    given_name
    family_name
    verified
    timezone
    created_at
    active_org_id
  }
}
    """

    def UpdateUser(self, user_id: str, changes: dict):
        query = gql(self._UpdateUserQuery)
        variables = {
            "user_id": user_id,
            "changes": changes,
        }
        operation_name = "UpdateUser"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateUserInfoQuery = """
    mutation UpdateUserInfo($id: String!, $given_name: String!, $family_name: String!) {
    update_Users_by_pk(pk_columns: {id: $id}, _set: {family_name: $family_name, given_name: $given_name}) {
        family_name
        given_name
        email
        id
        timezone
        verified
    }
}
    """

    def UpdateUserInfo(self, id: str, given_name: str, family_name: str):
        query = gql(self._UpdateUserInfoQuery)
        variables = {
            "id": id,
            "given_name": given_name,
            "family_name": family_name,
        }
        operation_name = "UpdateUserInfo"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )

    _UpdateUserVerificationStatusQuery = """
    mutation UpdateUserVerificationStatus($user_id: String!, $verified: Boolean!, $given_name: String!, $family_name: String!, $country_iso_code: String!) {
    update_Users(where: {id: {_eq: $user_id}}, _set: {verified: $verified, given_name: $given_name, family_name: $family_name, country_iso_code: $country_iso_code}) {
        returning {
            active_org_id
            country_iso_code
            created_at
            email
            family_name
            given_name
            id
        }
    }
}
    """

    def UpdateUserVerificationStatus(self, user_id: str, verified: bool, given_name: str, family_name: str, country_iso_code: str):
        query = gql(self._UpdateUserVerificationStatusQuery)
        variables = {
            "user_id": user_id,
            "verified": verified,
            "given_name": given_name,
            "family_name": family_name,
            "country_iso_code": country_iso_code,
        }
        operation_name = "UpdateUserVerificationStatus"
        operation_type = "write"
        return self.execute(
            query,
            variable_values=variables,
            operation_name=operation_name,
            operation_type=operation_type,
        )
