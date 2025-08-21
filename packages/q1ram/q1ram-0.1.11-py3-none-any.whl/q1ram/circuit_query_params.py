from pydantic import BaseModel


class QueryParams(BaseModel):
    number_address_bits:int
    number_data_bits:int
    address_value:list[int]|None
    data_value:list[int]|None