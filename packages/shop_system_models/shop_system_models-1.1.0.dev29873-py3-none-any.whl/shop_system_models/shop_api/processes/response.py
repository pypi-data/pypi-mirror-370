from shop_system_models.shop_api.processes.request import ProcessModel
from pydantic import BaseModel


class ProcessResponseModel(ProcessModel):
    id: str


class UpdateMessageResponseModel(BaseModel):
    text: str
    status: str
    order_number: str
