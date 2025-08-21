from nexus_auth.providers.base import OAuth2IdentityProvider, ProviderBuilder


class GoogleOAuth2Provider(OAuth2IdentityProvider):
    """Google OAuth2 provider."""

    def get_authorization_url(self):
        return "https://accounts.google.com/o/oauth2/v2/auth"

    def get_token_url(self):
        return "https://www.googleapis.com/oauth2/v4/token"


class GoogleOAuth2ProviderBuilder(ProviderBuilder):
    def __call__(self, client_id, client_secret, **_ignored):
        return GoogleOAuth2Provider(client_id, client_secret)
