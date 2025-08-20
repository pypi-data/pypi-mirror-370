from flask import Flask, request, jsonify
from threading import Thread
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.oauth2.rfc6749 import grants, BearerToken, ClientAuthentication
from authlib.oauth2 import OAuth2Request
import time


class InMemoryOAuthServer:
    def __init__(self, host="127.0.0.1", port=5001):
        self.host = host
        self.port = port
        self.clients = {}
        self.tokens = {}

        self.app = Flask(__name__)
        self._setup_routes()

        self.authorization = AuthorizationServer()
        self.authorization.init_app(
            self.app,
            query_client=self._query_client,
            client_authentication_class=self._ClientAuth(self.clients),
        )
        self.authorization.register_grant(self._ClientCredentialsGrant, [self._TokenGenerator(self.tokens)])

    # ---------------- Internal Grant Classes ----------------

    class _ClientCredentialsGrant(grants.ClientCredentialsGrant):
        def authenticate_client(self):
            return self.request.client

        def save_bearer_token(self, token, request):
            token["issued_at"] = int(time.time())
            self.server.tokens[token["access_token"]] = token

    class _ClientAuth(ClientAuthentication):
        def __init__(self, clients):
            self.clients = clients

        def authenticate(self, request: OAuth2Request, methods):
            client_id = request.client_id
            client = self.clients.get(client_id)
            if client and client.check_client_secret(request.client_secret):
                return client
            return None

    class _TokenGenerator(BearerToken):
        def __init__(self, token_store):
            super().__init__(None, None)
            self.token_store = token_store

    # ---------------- Internal Client Model ----------------

    class _Client:
        def __init__(self, client_id, client_secret, scope):
            self.client_id = client_id
            self.client_secret = client_secret
            self.scope = scope
            self.token_endpoint_auth_method = "client_secret_basic"
            self.grant_types = ["client_credentials"]
            self.response_types = []
            self.redirect_uris = []

        def check_client_secret(self, secret):
            return self.client_secret == secret

        def check_grant_type(self, grant_type):
            return grant_type == "client_credentials"
        

