
from airalogy.types import ATCG, CurrentTime, UserName
from pydantic import BaseModel

class DNA(BaseModel):
    seq: ATCG
    time: CurrentTime
    user: UserName

# m = DNA(seq="ATCGGATC")

s1 = DNA.model_json_schema()

print(s1)
