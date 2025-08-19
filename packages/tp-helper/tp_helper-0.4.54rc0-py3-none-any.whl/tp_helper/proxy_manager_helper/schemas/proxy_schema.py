from pydantic import BaseModel


class ProxySchema(BaseModel):
    login: str
    password: str
    ip: str
    port: int

    def __hash__(self):
        return hash((self.ip, self.port, self.login, self.password))
