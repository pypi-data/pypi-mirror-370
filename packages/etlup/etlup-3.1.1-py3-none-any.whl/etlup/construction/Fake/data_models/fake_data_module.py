from pydantic import BaseModel
class FakeDataModuleV0(BaseModel):
    crazy_name: str
    crazy_array: list[int]
    another_crazy_array: list[int]
