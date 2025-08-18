import os
import jwt
import hashlib
import json
from urllib.parse import quote

import requests

env_cred = {
    "prod": "AdminUser@SynapseMLFabricIntegration.onmicrosoft.com",
}

env_workload_host = {
    "daily": "pbipdailyeus2euap-daily.pbidedicated.windows.net",
    "dxt": "pbipdxtcuseuap1-dxt.pbidedicated.windows.net",
    "msit": "pbipmsitwcus23-msit.pbidedicated.windows.net",
}


env_onelake_new = {
    "edog": "onelake-int-edog.dfs.pbidedicated.windows-int.net",
    "daily": "daily-onelake.dfs.fabric.microsoft.com",
    "dxt": "dxt-onelake.dfs.fabric.microsoft.com",
    "msit": "msit-onelake.dfs.fabric.microsoft.com",
    "prod": "onelake.dfs.fabric.microsoft.com",
}


def get_bearer_token(env, username, password, audience="pbi"):
    if audience != "pbi" and audience != "storage":
        raise ValueError("Only pbi and storage audiences are supported.")

    # XMLA client id
    client_id = "cf710c6e-dfcc-4fa8-a093-d47294e44c66"
    user, tenant = username.split("@")

    if env == "edog":
        resource = "https://analysis.windows-int.net/powerbi/api"
        authority = "login.windows-ppe.net"
    else:
        resource = (
            "https://analysis.windows.net/powerbi/api"
            if audience == "pbi"
            else "https://storage.azure.com"
        )
        authority = "login.windows.net"

    login_url = f"https://{authority}/{tenant}/oauth2/token"
    payload = f'resource={quote(resource, safe="")}&client_id={client_id}&grant_type=password&username={username}&password={quote(password, safe="")}&scope=openid'
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "fpc=AlqdPsBZ3IhEkuEX2q3BHxjyrCATAQAAAAFta9sOAAAALbyONgEAAAAZbWvbDgAAAA; stsservicecookie=estsppe",
    }
    response = requests.request("GET", login_url, headers=headers, data=payload).json()
    try:
        token_type = response["token_type"]
    except Exception as e:
        print(f"Bad response: {response}")
        raise e

    if token_type != "Bearer":
        raise ValueError("The token received is not a bearer.")

    return response["access_token"]


def get_username_from_bearer_token(bearer_token: str):
    payload = jwt.decode(bearer_token, options={"verify_signature": False})
    return payload.get("upn")


class FabricAuthUtil:
    """
    # check if .fabric-token exists
    #    parse and done :)
    #
    # 1. get corpnet user token via "az login --use-device-code" to access keyvault
    # 2. get environment (edog/dxt/msit) username/password from keyvault
    # 3. get bearer token for environment username/password
    # 4. create workspace (re-use if exists)
    # 5. store the token in .fabric-token
    """

    env_bearer_token: dict[str, str] = dict()

    user_keyvaults = {
        "prod": {
            "vault": "SynapseMLFabricTestCreds",
            "secret-name": "AdminUser-SynapseMLFabricIntegration",
        }
    }

    def __init__(self, env: str):
        self.env = env

    def get_dev_user(self):
        """Returns the developer's username."""

        return get_username_from_bearer_token(self.get_env_bearer_token())

    def get_env_username(self) -> str:
        """Returns the username for the environment (edog/dxt/msit)."""
        return env_cred[self.env]

    def get_env_password(self):
        return os.environ.get("ut_password")

    def get_env_bearer_token(self, audience="pbi") -> str:
        """Returns the bearer token for the environment (edog/dxt/msit)."""

        if audience not in ["pbi", "storage"]:
            raise ValueError(f"audience must be either 'pbi' or 'storage': {audience}")

        # useful to test using a specific token
        # import base64
        # token = ""
        # bearer_token_fabric = base64.b64decode(token.encode('ascii')).decode('ascii')
        # return bearer_token_fabric

        # check our local cache
        token = self.env_bearer_token.get(audience)
        if token is not None:
            return token

        password = self.get_env_password()
        if password is None:
            # usually from dev box
            from msal import PublicClientApplication

            app = PublicClientApplication(
                # PowerBI
                "7f67af8a-fedc-4b08-8b4e-37c4d127b6cf",
                authority="https://login.microsoftonline.com/organizations",
            )

            for aud in ["pbi", "storage"]:
                if aud == "pbi":
                    scope = "https://analysis.windows.net/powerbi/api/.default"
                else:
                    scope = "https://storage.azure.com/.default"

                self.env_bearer_token[aud] = app.acquire_token_interactive(
                    scopes=[scope], port=12604
                )["access_token"]
        else:
            # usually from CI pipeline. Password is fetched from KeyVault via ADO task + ADO service connection
            username = self.get_env_username()
            # useful to retrieve username/password to interactively explore your workspace
            print(
                f"ENV: {self.env} USERNAME: {username} PASSWORD: {hashlib.md5(password.encode('utf-8')).hexdigest()}"
            )

            for aud in ["pbi", "storage"]:
                self.env_bearer_token[aud] = get_bearer_token(
                    self.env, username, password, aud
                )

        return self.env_bearer_token[audience]

    def _get_or_create_workspace(self, workspace_name: str):
        from sempy.fabric._client._workspace_client import WorkspaceClient
        from sempy.fabric.exceptions._exceptions import WorkspaceNotFoundException

        try:
            workspace_id = WorkspaceClient(workspace_name).get_workspace_id()
        except WorkspaceNotFoundException:
            # get Premium Per User (PPU) capacity
            # on MSIT this one allows for XMLA edit
            # alternative is FT1
            import sempy.fabric as fabric
            from sempy.fabric import list_capacities

            capacity_id = (
                list_capacities().query("Sku == 'FT1' or Sku == 'F64'")["Id"].values[0]
            )

            workspace_id = fabric.create_workspace(
                workspace_name, capacity_id=capacity_id
            )

        return workspace_id

    def _get_workspace_name(self):
        alias = self.get_dev_user().split("@")[0]
        ws = f"Assistant {alias}"

        # allow external override
        return os.environ.get("ut_workspace", ws)

    def get_fabric_config(self) -> dict[str, str]:
        from sempy.fabric._token_provider import (
            SynapseTokenProvider,
            _get_token_seconds_remaining,
        )

        cache_path = ".fabric-config"

        if os.path.exists(cache_path):
            fabric_config = json.loads(open(cache_path, "r").read())

            # rehydrate bearer token, so we can resolve the user name
            self.env_bearer_token = {
                "pbi": fabric_config["bearer_token"],
                "storage": fabric_config["bearer_storage_token"],
            }

            workspace_name = self._get_workspace_name()

            # check if token is still valid and if the workspace/identity matches
            # in case user was switching between environments/identities:
            token_seconds_remaining = _get_token_seconds_remaining(
                fabric_config["bearer_token"]
            )
            cached_workspace_name = fabric_config.get("workspace_name", None)

            if (
                token_seconds_remaining > 10 * 60
                and cached_workspace_name == workspace_name
            ):
                return fabric_config
            else:
                # delete expired or wrong token
                self.env_bearer_token = dict()

        # this will trigger auth locally as we need the bearer token
        workspace_name = self._get_workspace_name()

        # get token and patch SynapseTokenProvider so flat api works
        bearer_token_fabric = self.get_env_bearer_token()
        setattr(SynapseTokenProvider, "__call__", lambda _: bearer_token_fabric)

        workspace_id = self._get_or_create_workspace(workspace_name)

        print(f"WORKSPACE: {workspace_name} ({workspace_id})")

        fabric_config = {
            "bearer_token": bearer_token_fabric,
            "bearer_storage_token": self.get_env_bearer_token("storage"),
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
            "username": self.get_dev_user(),
        }

        # cache the token
        with open(cache_path, "w") as f:
            f.write(json.dumps(fabric_config, default=str))

        return fabric_config


def get_fabric_info():
    # need to disable telemetry to avoid triggering all of SynapseML-Utils initialization
    os.environ["REPORT_USAGE_TELEMETRY"] = "false"

    from sempy.fabric._environment import _on_fabric

    if _on_fabric():
        import sempy.fabric as fabric

        from notebookutils.credentials import (  # pyright: ignore[reportMissingImports]
            getToken,
        )

        bearer_token = getToken("pbi")

        workspace_id = fabric.get_workspace_id()
        workspace_name = fabric.resolve_workspace_name(workspace_id)

        fabric_info = {
            "bearer_token": bearer_token,
            "workspace_id": workspace_id,
            "workspace_name": workspace_name,
        }
    else:
        from sempy.fabric import _environment, list_workspaces

        # default to MSIT to support local box development
        # the build pipeline overrides w/ the correct environment
        env = os.environ.get("ut_env", "daily")
        _environment.environment = env

        fabric_info = FabricAuthUtil(env).get_fabric_config()

        workspace_id = fabric_info["workspace_id"]

        # still need to patch sempy environment
        def _local_get_trident_config(key: str) -> str:
            if key == "trident.workspace.id" or key == "trident.artifact.workspace.id":
                return fabric_info["workspace_id"]
            elif key == "trident.onelake.endpoint":
                return env_onelake_new[env]
            else:
                raise ValueError(f"Unsupported key '{key}'")

        setattr(_environment, "_get_trident_config", _local_get_trident_config)

        # must not import to early due to how things are setup
        from synapse.ml.internal_utils.session_utils import (
            set_fabric_context,
            get_fabric_context,
        )
        from synapse.ml.fabric.service_discovery import set_envs
        from synapse.ml.fabric.token_utils import TokenUtils

        # TODO: AI Skill naming to revisit later
        ctx = {
            "trident.aiskill.shared_host": env_workload_host[env],
            "trident.lakehouse.tokenservice.endpoint": f"https://{env_workload_host[env]}",
            # "trident.capacity.id": test_environment.capacity_id,
            "trident.artifact.workspace.id": workspace_id,
            # for some reason sempy is using that key to lookup the workspace id
            "currentWorkspaceId": workspace_id,
            # "trident.lakehouse.id": lakehouse_id,
            "trident.workspace.id": workspace_id,
            # "trident.artifact.id": test_environment.artifact_id,
            "spark.trident.pbienv": env,
            "trident.aiskill.env": "true",
            "fs.defaultFS": f"https://{env_onelake_new[env]}",
        }

        set_fabric_context(ctx)

        # 2. Set AAD token
        TokenUtils().AAD_TOKEN = fabric_info["bearer_token"]
        TokenUtils().ML_AAD_TOKEN = fabric_info["bearer_token"]

        # 3. Set envs
        set_envs()

        # automatically resolve capacity id, can only do it after the environment is setup so we can call Fabric
        capacity_id = list_workspaces(filter=f"id eq '{workspace_id}'").iloc[0][
            "Capacity Id"
        ]
        ctx["trident.capacity.id"] = capacity_id

        # need to update the context again
        set_fabric_context(ctx)
        set_envs()

    return fabric_info
