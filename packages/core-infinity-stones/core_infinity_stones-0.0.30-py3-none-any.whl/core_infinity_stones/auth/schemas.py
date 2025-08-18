from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

class Traits(BaseModel):
    phone: str

class Identity(BaseModel):
    id: str
    state: str
    state_changed_at: datetime
    created_at: datetime
    updated_at: datetime
    is_guest: bool
    traits: Optional[Traits] = None

class UserAuthResponse(BaseModel):
    id: str
    active: bool
    expires_at: datetime
    authenticated_at: datetime
    issued_at: datetime
    identity: Identity

class S2sToken(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    token_type: str

class S2sAuthResponse(BaseModel):
    active: bool
    client_id: str