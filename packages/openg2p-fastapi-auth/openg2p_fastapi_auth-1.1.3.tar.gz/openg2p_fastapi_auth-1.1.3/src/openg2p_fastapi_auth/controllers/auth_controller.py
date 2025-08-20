import base64
import hashlib
import logging
import secrets
import urllib.parse
from typing import Annotated

import httpx
import orjson
from fastapi import Depends, HTTPException, Response, status
from fastapi.responses import RedirectResponse
from jose import jwt
from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors.http_exceptions import InternalServerError

from ..config import Settings
from ..dependencies import JwtBearerAuth
from ..models.credentials import AuthCredentials
from ..models.login_provider import LoginProviderHttpResponse, LoginProviderResponse
from ..models.orm.login_provider import LoginProvider, LoginProviderTypes
from ..models.profile import BasicProfile
from ..models.provider_auth_parameters import OauthProviderParameters

_config = Settings.get_config(strict=False)
_logger = logging.getLogger(_config.logging_default_logger_name)


class AuthController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.router.prefix += "/auth"
        self.router.tags += ["auth"]

        self.router.add_api_route(
            "/profile",
            self.get_profile,
            responses={200: {"model": BasicProfile}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/logout",
            self.logout,
            methods=["POST"],
        )
        self.router.add_api_route(
            "/getLoginProviders",
            self.get_login_providers,
            responses={200: {"model": LoginProviderHttpResponse}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/getLoginProviderRedirect/{id}",
            self.get_login_provider_redirect,
            methods=["GET"],
        )

    async def get_profile(
        self,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        online: bool = True,
    ):
        """
        Get Profile Data of the authenticated user/entity.
        This can also be used to check whether or not the Authentication is present and valid.
        - Authentication required.
        - If online is true, the server will try to userinfo from original Authorization Server.
          Else it will return the information present in ID Token and Access token.
        """
        if online:
            provider = await self.get_login_provider_db_by_iss(auth.iss)
            if provider:
                if provider.type == LoginProviderTypes.oauth2_auth_code:
                    return BasicProfile.model_validate(
                        await self.get_oauth_validation_data(
                            auth, iss=auth.iss, provider=provider, combine=True
                        )
                    )
                else:
                    raise NotImplementedError()
        return BasicProfile.model_validate(auth.model_dump())

    async def logout(self, response: Response):
        """
        Perform Logout. This clears the Access Tokens and ID Tokens from cookies.
        - Authentication not mandatory.
        """
        response.delete_cookie("X-Access-Token")
        response.delete_cookie("X-ID-Token")

    async def get_login_providers(self):
        """
        Get available Login Providers List. Can also be used to display login providers on UI.
        Use getLoginProviderRedirect API to redirect to this Login Provider to perform login.
        """
        login_providers = await self.get_login_providers_db()
        return LoginProviderHttpResponse(
            loginProviders=[
                LoginProviderResponse(
                    id=lp.id,
                    name=lp.name,
                    type=lp.type,
                    displayName=lp.login_button_text,
                    displayIconUrl=lp.login_button_image_url,
                )
                for lp in login_providers
            ],
        )

    async def get_login_provider_redirect(self, id: int, redirect_uri: str = "/"):
        """
        Redirect URL to redirect to the Login Provider's Authorization URL
        based on the id of login provider given.
        """
        login_provider = None
        try:
            login_provider = await self.get_login_provider_db_by_id(id)
        except Exception as e:
            _logger.exception("Login Provider fetching: Invalid Id")
            # Instead of returning None, re-raise the exception to be handled by FastAPI
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Login Provider ID Not Found",
            ) from e

        if not login_provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Login Provider ID Not Found",
            )

        if login_provider.type == LoginProviderTypes.oauth2_auth_code:
            auth_parameters = OauthProviderParameters.model_validate(login_provider.authorization_parameters)
            authorize_query_params = {
                "client_id": auth_parameters.client_id,
                "response_type": auth_parameters.response_type,
                "redirect_uri": auth_parameters.redirect_uri,
                "scope": auth_parameters.scope,
                "nonce": secrets.token_urlsafe(),
                "state": orjson.dumps(
                    {
                        "p": login_provider.id,
                        "r": redirect_uri,
                    }
                ).decode(),
            }
            if auth_parameters.enable_pkce:
                await self.pkce_get_or_generate_code_verifier(login_provider)
                self.pkce_update_code_challenge(auth_parameters)
                authorize_query_params.update(
                    {
                        "code_challenge": auth_parameters.code_challenge,
                        "code_challenge_method": auth_parameters.code_challenge_method,
                    }
                )

            authorize_query_params.update(auth_parameters.extra_authorize_parameters)
            return RedirectResponse(
                f"{auth_parameters.authorize_endpoint}?{urllib.parse.urlencode(authorize_query_params)}"
            )
        else:
            raise NotImplementedError()

    async def pkce_get_or_generate_code_verifier(self, login_provider: LoginProvider) -> str:
        code_verifier = login_provider.authorization_parameters.get("code_verifier")
        if not code_verifier:
            code_verifier = secrets.token_urlsafe(32)
            login_provider.authorization_parameters["code_verifier"] = code_verifier
            await login_provider.update_to_db()
        return code_verifier

    def pkce_update_code_challenge(self, auth_params: OauthProviderParameters):
        if auth_params.code_challenge_method.lower() == "s256":
            auth_params.code_challenge = (
                base64.urlsafe_b64encode(hashlib.sha256(auth_params.code_verifier.encode("ascii")).digest())
                .rstrip(b"=")
                .decode()
            )

    async def get_login_providers_db(self) -> list[LoginProvider]:
        if _config.login_providers_list:
            lp_fields = LoginProvider.__mapper__.columns.keys()
            filtered_lps = []
            for lp in _config.login_providers_list:
                filtered_lps.append({lp_key: lp_val for lp_key, lp_val in lp.items() if lp_key in lp_fields})
            return [LoginProvider(**lp) for lp in filtered_lps]
        if await LoginProvider.table_exists_cached():
            return await LoginProvider.get_all()
        return []

    async def get_login_provider_db_by_id(self, id: int) -> LoginProvider:
        if _config.login_providers_list:
            lp_fields = LoginProvider.__mapper__.columns.keys()
            for lp in _config.login_providers_list:
                if id == lp.get("id"):
                    return LoginProvider(
                        **{lp_key: lp_val for lp_key, lp_val in lp.items() if lp_key in lp_fields}
                    )
            return None
        if await LoginProvider.table_exists_cached():
            return await LoginProvider.get_by_id(id)
        return None

    async def get_login_provider_db_by_iss(self, iss: str) -> LoginProvider:
        if _config.login_providers_list:
            lp_fields = LoginProvider.__mapper__.columns.keys()
            for lp in _config.login_providers_list:
                if iss == lp.get("iss"):
                    return LoginProvider(
                        **{lp_key: lp_val for lp_key, lp_val in lp.items() if lp_key in lp_fields}
                    )
            return None
        if await LoginProvider.table_exists_cached():
            return await LoginProvider.get_login_provider_from_iss(iss)
        return None

    async def get_oauth_validation_data(
        self,
        auth: str | AuthCredentials,
        id_token: str = None,
        iss: str = None,
        provider: LoginProvider = None,
        combine=True,
    ) -> dict:
        access_token = auth.credentials if isinstance(auth, AuthCredentials) else auth
        if not provider:
            if not iss:
                iss = jwt.get_unverified_claims(access_token)["iss"] if isinstance(auth, str) else auth.iss
            provider = await self.get_login_provider_db_by_iss(iss)
        # TODO: Check if provider is None
        auth_params = OauthProviderParameters.model_validate(provider.authorization_parameters)
        try:
            response = httpx.get(
                auth_params.validate_endpoint,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            if response.headers["content-type"].startswith("application/json"):
                res = response.json()
            elif response.headers["content-type"].startswith("application/jwt"):
                # jwks_cache.get().get(auth.iss),
                # TODO: Skipping this jwt validation. Some errors.
                res = jwt.get_unverified_claims(response.content)
            if combine:
                return JwtBearerAuth.combine_tokens(access_token, id_token, res)
            else:
                return res
        except Exception as e:
            _logger.exception("Error fetching user profile.")
            raise InternalServerError(
                "G2P-AUT-502",
                f"Error fetching userinfo. {repr(e)}",
            ) from e
