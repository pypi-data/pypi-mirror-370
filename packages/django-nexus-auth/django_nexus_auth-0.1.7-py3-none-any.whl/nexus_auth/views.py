from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from nexus_auth.exceptions import (
    NexusAuthBaseException,
    NoActiveProviderError,
    NoAssociatedUserError,
    UserNotActiveError,
    MissingEmailFromProviderError,
    EmailExtractionError,
)
from nexus_auth.serializers import (
    OAuth2ExchangeSerializer,
)
from nexus_auth.settings import nexus_settings
from nexus_auth.utils import build_oauth_provider
from nexus_auth.providers.base import OAuth2IdentityProvider
from typing import Optional

User = get_user_model()


class OAuthProvidersView(APIView):
    """View to get the providers"""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """
        Retrieve active providers with authorization URLs.
        """
        providers_config = nexus_settings.get_providers_config(request=request) or {}
        providers = []

        for provider_type, _ in providers_config.items():
            provider = build_oauth_provider(provider_type, providers_config)
            if provider:
                providers.append(
                    {
                        "type": provider_type,
                        "auth_url": provider.build_auth_url(),
                    }
                )

        return Response({"providers": providers}, status=200)


class OAuthExchangeView(APIView):
    """View to exchange the authorization code with the active provider for JWT tokens."""

    permission_classes = (AllowAny,)

    def post(self, request: Request, provider_type: str) -> Response:
        """

        Args:
            request: HTTP request containing the authorization code
            provider_type: Type of provider to use

        Returns:
            Response: JWT tokens (refresh and access)

        Raises:
            NoActiveProviderError: If no active provider is found
            MissingEmailFromProviderError: If no email is returned from the provider
            NoAssociatedUserError: If no user is associated with the provider
            UserNotActiveError: If the user is not active
            EmailExtractionError: If the email cannot be extracted from the provider
        """
        serializer = OAuth2ExchangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.authenticate_user_with_provider(
            request,
            provider_type,
            serializer.validated_data["code"],
            serializer.validated_data["code_verifier"],
            serializer.validated_data["redirect_uri"],
        )
        if not user.is_active:
            raise UserNotActiveError()

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token

        # Trigger user_logged_in signal
        user_logged_in.send(sender=self.__class__, request=request, user=user)

        return Response(
            {"refresh": str(refresh_token), "access": str(access_token)}, status=200
        )

    def authenticate_user_with_provider(
        self,
        request: Request,
        provider_type: str,
        authorization_code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> User:
        """Exchange the authorization code with the IdP and return the associated user object

        Args:
            request: HTTP request containing the authorization code
            provider_type: Type of provider to use
            authorization_code: Authorization code
            code_verifier: Code verifier
            redirect_uri: Redirect URI

        Returns:
            User: User associated with the authorization code

        Raises:
            NoActiveProviderError: If no active provider is found
            MissingEmailFromProviderError: If no email is returned from the provider
            NoAssociatedUserError: If no user is associated with the provider
            EmailExtractionError: If the email cannot be extracted from the provider
        """
        providers_config = nexus_settings.get_providers_config(request=request)
        provider: Optional[OAuth2IdentityProvider] = build_oauth_provider(
            provider_type, providers_config
        )
        if not provider:
            raise NoActiveProviderError()

        try:
            email: Optional[str] = provider.exchange_code_for_email(
                authorization_code=authorization_code,
                code_verifier=code_verifier,
                redirect_uri=redirect_uri,
            )
        except NexusAuthBaseException as e:
            raise EmailExtractionError() from e

        if not email:
            raise MissingEmailFromProviderError()

        try:
            # Match the email case-insensitively
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as e:
            raise NoAssociatedUserError() from e

        return user
