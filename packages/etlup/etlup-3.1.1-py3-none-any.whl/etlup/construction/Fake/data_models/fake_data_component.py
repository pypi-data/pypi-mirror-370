from pydantic import BaseModel
class FakeDataComponentV0(BaseModel):
    a_silly_string: str
    a_silly_integer: int
    a_silly_array: list[int]