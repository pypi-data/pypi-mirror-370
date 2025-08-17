from pydantic import BaseModel   

class JwtModel(BaseModel):
    secret_key:str
    algorithms: str
    audience: str
    issuer: str