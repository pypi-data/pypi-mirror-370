__version__ = "v1.35.0"
import json
import requests
from gql import Client as GqlClient
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportQueryError
from jose import jwt, exceptions
from datetime import datetime, timedelta
from typing import Optional
from kivera.cloudtenants import CloudTenantsMethods
from kivera.compliancemappings import ComplianceMappingsMethods
from kivera.config import ConfigMethods
from kivera.counters import CountersMethods
from kivera.domainacls import DomainACLsMethods
from kivera.globalpolicyfunctions import GlobalPolicyFunctionsMethods
from kivera.globalservices import GlobalServicesMethods
from kivera.identities import IdentitiesMethods
from kivera.identityprofiles import IdentityProfilesMethods
from kivera.managedrules import ManagedRulesMethods
from kivera.memberships import MembershipsMethods
from kivera.metrics import MetricsMethods
from kivera.organizationpolicyfunctions import OrganizationPolicyFunctionsMethods
from kivera.organizations import OrganizationsMethods
from kivera.plans import PlansMethods
from kivera.profiles import ProfilesMethods
from kivera.providerversions import ProviderVersionsMethods
from kivera.providers import ProvidersMethods
from kivera.proxies import ProxiesMethods
from kivera.proxyapikeys import ProxyApiKeysMethods
from kivera.proxydeployments import ProxyDeploymentsMethods
from kivera.proxyproviders import ProxyProvidersMethods
from kivera.roles import RolesMethods
from kivera.ruledependencies import RuleDependenciesMethods
from kivera.ruledependencyresources import RuleDependencyResourcesMethods
from kivera.ruleparameters import RuleParametersMethods
from kivera.rules import RulesMethods
from kivera.services import ServicesMethods
from kivera.userapikeys import UserApiKeysMethods
from kivera.users import UsersMethods

class ClientError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

class Client(
    GqlClient,
    CloudTenantsMethods,
	ComplianceMappingsMethods,
	ConfigMethods,
	CountersMethods,
	DomainACLsMethods,
	GlobalPolicyFunctionsMethods,
	GlobalServicesMethods,
	IdentitiesMethods,
	IdentityProfilesMethods,
	ManagedRulesMethods,
	MembershipsMethods,
	MetricsMethods,
	OrganizationPolicyFunctionsMethods,
	OrganizationsMethods,
	PlansMethods,
	ProfilesMethods,
	ProviderVersionsMethods,
	ProvidersMethods,
	ProxiesMethods,
	ProxyApiKeysMethods,
	ProxyDeploymentsMethods,
	ProxyProvidersMethods,
	RolesMethods,
	RuleDependenciesMethods,
	RuleDependencyResourcesMethods,
	RuleParametersMethods,
	RulesMethods,
	ServicesMethods,
	UserApiKeysMethods,
	UsersMethods
):

    def __init__(self, credentials={}, url="", headers={}, timeout=30):
        if type(credentials) != dict:
            raise Exception("invalid parameter: credentials must be a dictionary")

        if type(headers) != dict:
            raise Exception("invalid parameter: headers must be a dictionary")

        self.headers = headers
        self.headers['content-type'] = 'application/json'

        self._gql_endpoint = url
        self._credentials = credentials
        self._token = None
        self._jwks_key = None
        self.context = {}

        self._extract_auth_token()

        if not self._token and self._credentials:
            self._refresh_token()

        if self._token:
            self._verify_token()

        if not self._gql_endpoint:
            raise Exception("invalid parameter: url must be provided")

        GqlClient.__init__(self, transport=self._get_transport(), execute_timeout=timeout)

    def execute(self, query, variable_values: Optional[dict]=None, operation_name: Optional[str]=None, operation_type: Optional[str]=None):

        if self._token:
            try:
                self._verify_token()

            except exceptions.ExpiredSignatureError:
                if not self._credentials:
                    raise ClientError("invalid token: token expired")
                self._refresh_token()
                self._verify_token()
                self.transport = self._get_transport()

            except exceptions.JWTError:
                raise ClientError("invalid signature")
            except Exception as e:
                raise ClientError(str(e))

        try:
            extra_args = { "headers": { "X-Kivera-Operation-Type": operation_type } }
            resp = GqlClient.execute(self, query, variable_values=variable_values, operation_name=operation_name, extra_args=extra_args)

        except TransportQueryError as e:
            if str(e).find("not found in type"):
                raise ClientError("access denied") from None
            else:
                raise ClientError(str(e))
        except Exception as e:
            raise ClientError(str(e))

        return resp

    def _extract_auth_token(self):
        auth_header = self.headers.get('authorization', self.headers.get('Authorization', ""))
        parts = auth_header.split(' ')
        if len(parts) == 2 and parts[0] == "Bearer":
            self._token = parts[1]

    def _get_transport(self):
        self.headers['authorization'] = f'Bearer {self._token}'
        return AIOHTTPTransport(url=self._gql_endpoint, headers=self.headers)

    def _refresh_token(self):
        authDomain = self._credentials.get('auth0_domain')
        url = f"https://{authDomain}/oauth/token"

        auth_config = json.dumps({
            "client_id": self._credentials['client_id'],
            "client_secret": self._credentials['client_secret'],
            "audience": self._credentials['audience'],
            "grant_type": "client_credentials",
        })

        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=auth_config, headers=headers)

        if not response.ok:
            raise ClientError(response.text)

        self._token = json.loads(response.text).get('access_token')

    def _verify_token(self):
        claims_unverified = jwt.get_unverified_claims(self._token)
        self._auth_endpoint = claims_unverified["iss"]
        if not self._auth_endpoint.endswith('.kivera.io/'):
            raise ClientError("invalid token: incorrect issuer")

        audience = self._auth_endpoint.replace("https://auth.", "https://api.") + "v1/graphql"

        if not self._gql_endpoint:
            self._gql_endpoint = audience

        self._refresh_jwks_key()
        claims = jwt.decode(token=self._token, key=self._jwks_key, audience=audience)
        for k, v in claims.get('https://hasura.io/jwt/claims', {}).items():
            if k.startswith('x-hasura-'):
                k = k[len('x-hasura-'):]
            if k == 'org-id':
                v = int(v)
            self.context[k] = v

    def _refresh_jwks_key(self):
        if self._jwks_key and datetime.now() < self._jwks_refresh:
            return

        response = requests.get(url=f"{self._auth_endpoint}.well-known/jwks.json")
        if not response.ok:
            raise ClientError(response.text)

        self._jwks_key = json.loads(response.text)
        self._jwks_refresh = datetime.now() + timedelta(hours=24)
