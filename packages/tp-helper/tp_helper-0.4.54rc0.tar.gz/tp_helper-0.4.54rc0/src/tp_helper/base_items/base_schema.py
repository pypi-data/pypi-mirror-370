from pydantic import BaseModel


class BaseSchema(BaseModel):
    def to_json(self):
        return self.model_dump_json()
