from pydantic import BaseModel


class AuthConfig(BaseModel):
    auth_service_base_url: str
    authenticate_user_endpoint_path: str
    generate_s2s_token_endpoint_path: str
    authenticate_s2s_token_endpoint_path: str
