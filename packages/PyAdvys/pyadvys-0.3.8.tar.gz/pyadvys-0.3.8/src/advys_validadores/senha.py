from pydantic import BaseModel, SecretStr

class SenhaSimples(BaseModel):
    valor: SecretStr