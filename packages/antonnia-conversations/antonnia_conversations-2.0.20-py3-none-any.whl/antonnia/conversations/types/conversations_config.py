from typing import Literal, Union
from datetime import datetime
from pydantic import BaseModel

ConfigKeys = Literal["session.autoclose.after_inactivity", "session.recovery.after_inactivity"]

class SessionAutoCloseAfterInactivityConfig(BaseModel):
    type: Literal["session.autoclose.after_inactivity"]
    expires_in_minutes: int

Config = Union[
    SessionAutoCloseAfterInactivityConfig
]

class ConversationsConfig(BaseModel):
  key: ConfigKeys
  organization_id: str
  config: Config
  created_at: datetime
  updated_at: datetime


    
    
    