"""Service Factory (Factry Pattern for dependcy resolution)"""

import asyncpg
from app.repositories.api_key_repo import APIKeyRepository
from app.services.auth_service import AuthService

class ServiceFactory:
    @staticmethod
    def get_auth_service(conn: asyncpg.Connection) -> AuthService:
        repo = APIKeyRepository(conn)
        return AuthService(api_key_repo=repo)
    