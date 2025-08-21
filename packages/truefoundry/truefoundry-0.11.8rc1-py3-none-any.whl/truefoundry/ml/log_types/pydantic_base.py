from truefoundry.pydantic_v1 import BaseModel


class PydanticBase(BaseModel):
    # I can make this a property,
    # but <3.9, it is difficult to access
    # property from classmethod
    @staticmethod
    def get_log_type() -> str:
        raise NotImplementedError()
