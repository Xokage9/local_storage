from app.config import settings


class KeycloakClient:
    def __init__(self) -> None:
        self.base_url = settings.keycloak_url
        self.realm = settings.keycloak_realm
        self.client_id = settings.keycloak_client_id
        self.client_secret = settings.keycloak_client_secret

    @property
    def auth_url(self) -> str:
        return (
            f"{self.base_url}/realms/{self.realm}"
            f"/protocol/openid-connect/auth"
        )

    @property
    def token_url(self) -> str:
        return (
            f"{self.base_url}/realms/{self.realm}"
            f"/protocol/openid-connect/token"
        )

    @property
    def logout_url(self) -> str:
        return (
            f"{self.base_url}/realms/{self.realm}"
            f"/protocol/openid-connect/logout"
        )

    @property
    def userinfo_url(self) -> str:
        return (
            f"{self.base_url}/realms/{self.realm}"
            f"/protocol/openid-connect/userinfo"
        )

    def get_openid_config(self) -> dict:
        return {
            "auth_url": self.auth_url,
            "token_url": self.token_url,
            "logout_url": self.logout_url,
            "client_id": self.client_id,
            "realm": self.realm,
        }


keycloak_client = KeycloakClient()
